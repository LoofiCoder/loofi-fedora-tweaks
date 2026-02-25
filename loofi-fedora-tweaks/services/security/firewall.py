"""Firewall Manager — firewalld backend with daemon-first IPC."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from typing import List

from services.ipc import daemon_client
from utils.commands import PrivilegedCommand

logger = logging.getLogger(__name__)


@dataclass
class FirewallInfo:
    """Snapshot of current firewall state."""

    running: bool = False
    default_zone: str = ""
    active_zones: dict = field(default_factory=dict)
    ports: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    rich_rules: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "running": self.running,
            "default_zone": self.default_zone,
            "active_zones": self.active_zones,
            "ports": self.ports,
            "services": self.services,
            "rich_rules": self.rich_rules,
        }


@dataclass
class FirewallResult:
    """Result of firewall write operation."""

    success: bool
    message: str


@dataclass
class ZoneInfo:
    """CLI-compatible zone snapshot."""

    name: str
    active: bool


class FirewallManager:
    """Interface to firewalld with daemon-first fallback."""
    _available_cached: bool | None = None
    _available_cache_run_id: int | None = None

    @classmethod
    def is_available(cls) -> bool:
        run_id = id(subprocess.run)
        if cls._available_cached is not None and cls._available_cache_run_id == run_id:
            return cls._available_cached
        try:
            result = subprocess.run(["firewall-cmd", "--version"], capture_output=True, text=True, timeout=5)
            cls._available_cached = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            cls._available_cached = False
        cls._available_cache_run_id = run_id
        return cls._available_cached

    @classmethod
    def is_running(cls) -> bool:
        return cls.is_running_local()

    @classmethod
    def get_status(cls) -> FirewallInfo:
        data = daemon_client.call_json("FirewallGetStatus")
        if isinstance(data, dict):
            return FirewallInfo(
                running=bool(data.get("running", False)),
                default_zone=str(data.get("default_zone", "")),
                active_zones=data.get("active_zones", {}) or {},
                ports=[str(x) for x in (data.get("ports", []) or [])],
                services=[str(x) for x in (data.get("services", []) or [])],
                rich_rules=[str(x) for x in (data.get("rich_rules", []) or [])],
            )
        return cls._get_status_legacy()

    @classmethod
    def get_status_local(cls) -> FirewallInfo:
        info = FirewallInfo()
        info.running = cls.is_running()
        if not info.running:
            return info
        info.default_zone = cls.get_default_zone()
        info.active_zones = cls.get_active_zones()
        info.ports = cls.list_ports()
        info.services = cls.list_services()
        info.rich_rules = cls.list_rich_rules()
        return info

    @classmethod
    def _get_status_legacy(cls) -> FirewallInfo:
        """Legacy status flow used by tests and fallback mode."""
        info = FirewallInfo()
        info.running = cls.is_running()
        if not info.running:
            return info
        info.default_zone = cls.get_default_zone()
        info.active_zones = cls.get_active_zones()
        info.ports = cls.list_ports()
        info.services = cls.list_services()
        info.rich_rules = cls.list_rich_rules()
        return info

    @classmethod
    def is_running_local(cls) -> bool:
        try:
            result = subprocess.run(["firewall-cmd", "--state"], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() == "running"
        except (OSError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def get_default_zone(cls) -> str:
        data = daemon_client.call_json("FirewallGetDefaultZone")
        if isinstance(data, str):
            return data
        return cls.get_default_zone_local()

    @classmethod
    def get_default_zone_local(cls) -> str:
        try:
            result = subprocess.run(["firewall-cmd", "--get-default-zone"], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else ""
        except (OSError, subprocess.TimeoutExpired):
            return ""

    @classmethod
    def get_zones(cls) -> List[str]:
        data = daemon_client.call_json("FirewallGetZones")
        if isinstance(data, list):
            return [str(x) for x in data]
        return cls.get_zones_local()

    @classmethod
    def get_zones_local(cls) -> List[str]:
        try:
            result = subprocess.run(["firewall-cmd", "--get-zones"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split()
            return []
        except (OSError, subprocess.TimeoutExpired):
            return []

    @classmethod
    def get_active_zones(cls) -> dict:
        data = daemon_client.call_json("FirewallGetActiveZones")
        if isinstance(data, dict):
            parsed: dict[str, list[str]] = {}
            for zone, values in data.items():
                if not isinstance(zone, str):
                    continue
                if isinstance(values, list):
                    parsed[zone] = [str(item) for item in values]
                else:
                    parsed[zone] = []
            return parsed
        return cls.get_active_zones_local()

    @classmethod
    def get_active_zones_local(cls) -> dict:
        try:
            result = subprocess.run(["firewall-cmd", "--get-active-zones"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return {}
            zones: dict[str, list[str]] = {}
            current_zone = None
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("interfaces:") or line.startswith("sources:"):
                    if current_zone:
                        ifaces = line.split(":", 1)[1].strip().split()
                        zones.setdefault(current_zone, []).extend(ifaces)
                else:
                    current_zone = line
                    zones.setdefault(current_zone, [])
            return zones
        except (OSError, subprocess.TimeoutExpired):
            return {}

    @classmethod
    def list_ports(cls, zone: str = "") -> List[str]:
        data = daemon_client.call_json("FirewallListPorts", zone)
        if isinstance(data, list):
            return [str(x) for x in data]
        return cls.list_ports_local(zone)

    @classmethod
    def list_ports_local(cls, zone: str = "") -> List[str]:
        try:
            cmd = ["firewall-cmd", "--list-ports"]
            if zone:
                cmd.extend(["--zone", zone])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split()
            return []
        except (OSError, subprocess.TimeoutExpired):
            return []

    @classmethod
    def list_services(cls, zone: str = "") -> List[str]:
        data = daemon_client.call_json("FirewallListServices", zone)
        if isinstance(data, list):
            return [str(x) for x in data]
        return cls.list_services_local(zone)

    @classmethod
    def list_services_local(cls, zone: str = "") -> List[str]:
        try:
            cmd = ["firewall-cmd", "--list-services"]
            if zone:
                cmd.extend(["--zone", zone])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return sorted(result.stdout.strip().split())
            return []
        except (OSError, subprocess.TimeoutExpired):
            return []

    @classmethod
    def get_available_services(cls) -> List[str]:
        try:
            result = subprocess.run(["firewall-cmd", "--get-services"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return sorted(result.stdout.strip().split())
            return []
        except (OSError, subprocess.TimeoutExpired):
            return []

    @classmethod
    def open_port(cls, port: str, protocol: str = "tcp", zone: str = "", permanent: bool = True) -> FirewallResult:
        data = daemon_client.call_json("FirewallOpenPort", port, protocol, zone, bool(permanent))
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.open_port_local(port, protocol, zone, permanent)

    @classmethod
    def open_port_local(cls, port: str, protocol: str = "tcp", zone: str = "", permanent: bool = True) -> FirewallResult:
        port_spec = f"{port}/{protocol}"
        try:
            cmd = ["pkexec", "firewall-cmd", f"--add-port={port_spec}"]
            if zone:
                cmd.extend(["--zone", zone])
            if permanent:
                cmd.append("--permanent")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                if permanent:
                    cls._reload()
                return FirewallResult(True, f"Opened port {port_spec}")
            return FirewallResult(False, f"Failed to open {port_spec}: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def close_port(cls, port: str, protocol: str = "tcp", zone: str = "", permanent: bool = True) -> FirewallResult:
        data = daemon_client.call_json("FirewallClosePort", port, protocol, zone, bool(permanent))
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.close_port_local(port, protocol, zone, permanent)

    @classmethod
    def close_port_local(cls, port: str, protocol: str = "tcp", zone: str = "", permanent: bool = True) -> FirewallResult:
        port_spec = f"{port}/{protocol}"
        try:
            cmd = ["pkexec", "firewall-cmd", f"--remove-port={port_spec}"]
            if zone:
                cmd.extend(["--zone", zone])
            if permanent:
                cmd.append("--permanent")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                if permanent:
                    cls._reload()
                return FirewallResult(True, f"Closed port {port_spec}")
            return FirewallResult(False, f"Failed to close {port_spec}: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def add_service(cls, service: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        data = daemon_client.call_json("FirewallAddService", service, zone, bool(permanent))
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.add_service_local(service, zone, permanent)

    @classmethod
    def add_service_local(cls, service: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        try:
            cmd = ["pkexec", "firewall-cmd", f"--add-service={service}"]
            if zone:
                cmd.extend(["--zone", zone])
            if permanent:
                cmd.append("--permanent")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                if permanent:
                    cls._reload()
                return FirewallResult(True, f"Added service {service}")
            return FirewallResult(False, f"Failed to add {service}: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def remove_service(cls, service: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        data = daemon_client.call_json("FirewallRemoveService", service, zone, bool(permanent))
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.remove_service_local(service, zone, permanent)

    @classmethod
    def remove_service_local(cls, service: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        try:
            cmd = ["pkexec", "firewall-cmd", f"--remove-service={service}"]
            if zone:
                cmd.extend(["--zone", zone])
            if permanent:
                cmd.append("--permanent")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                if permanent:
                    cls._reload()
                return FirewallResult(True, f"Removed service {service}")
            return FirewallResult(False, f"Failed to remove {service}: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def list_rich_rules(cls, zone: str = "") -> List[str]:
        data = daemon_client.call_json("FirewallListRichRules", zone)
        if isinstance(data, list):
            return [str(x) for x in data]
        return cls.list_rich_rules_local(zone)

    @classmethod
    def list_rich_rules_local(cls, zone: str = "") -> List[str]:
        try:
            cmd = ["firewall-cmd", "--list-rich-rules"]
            if zone:
                cmd.extend(["--zone", zone])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().splitlines()
            return []
        except (OSError, subprocess.TimeoutExpired):
            return []

    @classmethod
    def start_firewall(cls) -> FirewallResult:
        data = daemon_client.call_json("FirewallStart")
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.start_firewall_local()

    @classmethod
    def start_firewall_local(cls) -> FirewallResult:
        try:
            binary, args, _ = PrivilegedCommand.systemctl("start", "firewalld")
            result = subprocess.run([binary] + args, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return FirewallResult(True, "Firewall started")
            return FirewallResult(False, f"Failed: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def stop_firewall(cls) -> FirewallResult:
        data = daemon_client.call_json("FirewallStop")
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.stop_firewall_local()

    @classmethod
    def stop_firewall_local(cls) -> FirewallResult:
        try:
            binary, args, _ = PrivilegedCommand.systemctl("stop", "firewalld")
            result = subprocess.run([binary] + args, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return FirewallResult(True, "Firewall stopped")
            return FirewallResult(False, f"Failed: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def set_default_zone(cls, zone: str) -> FirewallResult:
        data = daemon_client.call_json("FirewallSetDefaultZone", zone)
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.set_default_zone_local(zone)

    @classmethod
    def set_default_zone_local(cls, zone: str) -> FirewallResult:
        try:
            result = subprocess.run(["pkexec", "firewall-cmd", f"--set-default-zone={zone}"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return FirewallResult(True, f"Default zone set to {zone}")
            return FirewallResult(False, f"Failed: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def add_rich_rule(cls, rule: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        data = daemon_client.call_json("FirewallAddRichRule", rule, zone, bool(permanent))
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.add_rich_rule_local(rule, zone, permanent)

    @classmethod
    def add_rich_rule_local(cls, rule: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        try:
            cmd = ["pkexec", "firewall-cmd", f"--add-rich-rule={rule}"]
            if zone:
                cmd.extend(["--zone", zone])
            if permanent:
                cmd.append("--permanent")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                if permanent:
                    cls._reload()
                return FirewallResult(True, "Added rich rule")
            return FirewallResult(False, f"Failed to add rich rule: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    @classmethod
    def remove_rich_rule(cls, rule: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        data = daemon_client.call_json("FirewallRemoveRichRule", rule, zone, bool(permanent))
        if isinstance(data, dict):
            return FirewallResult(success=bool(data.get("success", False)), message=str(data.get("message", "")))
        return cls.remove_rich_rule_local(rule, zone, permanent)

    @classmethod
    def remove_rich_rule_local(cls, rule: str, zone: str = "", permanent: bool = True) -> FirewallResult:
        try:
            cmd = ["pkexec", "firewall-cmd", f"--remove-rich-rule={rule}"]
            if zone:
                cmd.extend(["--zone", zone])
            if permanent:
                cmd.append("--permanent")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                if permanent:
                    cls._reload()
                return FirewallResult(True, "Removed rich rule")
            return FirewallResult(False, f"Failed to remove rich rule: {result.stderr.strip()}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            return FirewallResult(False, f"Error: {exc}")

    # CLI compatibility aliases
    @classmethod
    def list_zones(cls) -> list[ZoneInfo]:
        zones = cls.get_zones()
        active = cls.get_active_zones()
        return [ZoneInfo(name=z, active=z in active) for z in zones]

    @classmethod
    def add_port(cls, port_spec: str, zone: str = "") -> FirewallResult:
        if "/" in port_spec:
            port, protocol = port_spec.split("/", 1)
        else:
            port, protocol = port_spec, "tcp"
        return cls.open_port(port, protocol, zone)

    @classmethod
    def remove_port(cls, port_spec: str, zone: str = "") -> FirewallResult:
        if "/" in port_spec:
            port, protocol = port_spec.split("/", 1)
        else:
            port, protocol = port_spec, "tcp"
        return cls.close_port(port, protocol, zone)

    @classmethod
    def reload(cls) -> FirewallResult:
        reloaded = cls._reload()
        return FirewallResult(reloaded, "Reloaded firewall" if reloaded else "Failed to reload firewall")

    @classmethod
    def _reload(cls) -> bool:
        try:
            result = subprocess.run(["pkexec", "firewall-cmd", "--reload"], capture_output=True, text=True, timeout=15)
            return result.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def _reload_local(cls) -> bool:
        # Backward-compatible alias for older call sites.
        return cls._reload()
