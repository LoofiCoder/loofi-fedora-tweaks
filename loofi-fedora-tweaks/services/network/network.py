"""Network utility functions for daemon-first NetworkManager operations."""

from __future__ import annotations

import subprocess
from typing import List, Optional, Tuple

from services.ipc import daemon_client
from utils.log import get_logger

logger = get_logger(__name__)


class NetworkUtils:
    """Static utility methods for NetworkManager operations."""

    @staticmethod
    def scan_wifi() -> List[Tuple[str, str, str, str]]:
        data = daemon_client.call_json("NetworkScanWifi")
        if isinstance(data, list):
            rows: List[Tuple[str, str, str, str]] = []
            for row in data:
                if not isinstance(row, dict):
                    continue
                rows.append(
                    (
                        str(row.get("ssid", "")),
                        str(row.get("signal", "")),
                        str(row.get("security", "")),
                        str(row.get("active", "")),
                    )
                )
            return rows
        return NetworkUtils.scan_wifi_local()

    @staticmethod
    def scan_wifi_local() -> List[Tuple[str, str, str, str]]:
        """Local fallback for scanning Wi-Fi networks."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,ACTIVE", "device", "wifi", "list", "--rescan", "yes"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            rows: List[Tuple[str, str, str, str]] = []
            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue
                parts = line.split(":")
                if len(parts) >= 4:
                    ssid = parts[0] or "(Hidden)"
                    signal = f"{parts[1]}%"
                    security = parts[2] or "Open"
                    active = "Connected" if parts[3] == "yes" else ""
                    rows.append((ssid, signal, security, active))
            return rows
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("WiFi scan failed: %s", e)
            return []

    @staticmethod
    def load_vpn_connections() -> List[Tuple[str, str, str]]:
        data = daemon_client.call_json("NetworkLoadVpnConnections")
        if isinstance(data, list):
            rows: List[Tuple[str, str, str]] = []
            for row in data:
                if not isinstance(row, dict):
                    continue
                rows.append(
                    (
                        str(row.get("name", "")),
                        str(row.get("type", "")),
                        str(row.get("status", "")),
                    )
                )
            return rows
        return NetworkUtils.load_vpn_connections_local()

    @staticmethod
    def load_vpn_connections_local() -> List[Tuple[str, str, str]]:
        """Local fallback for VPN listing."""
        try:
            result = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE,ACTIVE", "connection", "show"], capture_output=True, text=True, timeout=5)
            rows: List[Tuple[str, str, str]] = []
            for line in result.stdout.strip().splitlines():
                lower = line.lower()
                if "vpn" in lower or "wireguard" in lower or "openvpn" in lower:
                    parts = line.split(":")
                    if len(parts) >= 3:
                        name = parts[0]
                        conn_type = parts[1]
                        status = "🟢 Active" if parts[2] == "yes" else "Inactive"
                        rows.append((name, conn_type, status))
            return rows
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to load VPN: %s", e)
            return []

    @staticmethod
    def detect_current_dns() -> str:
        data = daemon_client.call_json("NetworkDetectCurrentDns")
        if isinstance(data, str):
            return data
        return NetworkUtils.detect_current_dns_local()

    @staticmethod
    def detect_current_dns_local() -> str:
        """Local fallback for DNS detection."""
        try:
            result = subprocess.run(["nmcli", "-t", "-f", "IP4.DNS", "device", "show"], capture_output=True, text=True, timeout=5)
            dns_servers = set()
            for line in result.stdout.splitlines():
                if ":" in line:
                    val = line.split(":", 1)[1].strip()
                    if val:
                        dns_servers.add(val)
            if dns_servers:
                return ", ".join(sorted(dns_servers))
            return ""
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to detect DNS: %s", e)
            return ""

    @staticmethod
    def get_active_connection() -> Optional[str]:
        data = daemon_client.call_json("NetworkGetActiveConnection")
        if isinstance(data, str):
            return data or None
        return NetworkUtils.get_active_connection_local()

    @staticmethod
    def get_active_connection_local() -> Optional[str]:
        """Local fallback for active connection lookup."""
        try:
            res = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active"], capture_output=True, text=True, timeout=5)
            for line in res.stdout.splitlines():
                if "wifi" in line or "ethernet" in line:
                    return line.split(":")[0]
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to get active connection: %s", e)
        return None

    @staticmethod
    def check_hostname_privacy(connection_name: str) -> Optional[bool]:
        data = daemon_client.call_json("NetworkCheckHostnamePrivacy", connection_name)
        if isinstance(data, bool):
            return data
        return NetworkUtils.check_hostname_privacy_local(connection_name)

    @staticmethod
    def check_hostname_privacy_local(connection_name: str) -> Optional[bool]:
        """Local fallback for DHCP hostname privacy check."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "ipv4.dhcp-send-hostname", "connection", "show", connection_name], capture_output=True, text=True, timeout=5
            )
            val = result.stdout.strip().split(":")[-1].strip() if result.stdout.strip() else ""
            return val == "no"
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to check hostname privacy: %s", e)
            return None

    @staticmethod
    def reactivate_connection(connection_name: str) -> bool:
        data = daemon_client.call_json("NetworkReactivateConnection", connection_name)
        if isinstance(data, bool):
            return data
        return NetworkUtils.reactivate_connection_local(connection_name)

    @staticmethod
    def reactivate_connection_local(connection_name: str) -> bool:
        """Local fallback for connection reactivation."""
        try:
            subprocess.run(["nmcli", "con", "up", connection_name], capture_output=True, timeout=10)
            return True
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to reactivate connection: %s", e)
            return False

    @staticmethod
    def connect_wifi(ssid: str) -> bool:
        data = daemon_client.call_json("NetworkConnectWifi", ssid)
        if isinstance(data, bool):
            return data
        return NetworkUtils.connect_wifi_local(ssid)

    @staticmethod
    def connect_wifi_local(ssid: str) -> bool:
        """Local fallback for connecting to Wi-Fi by SSID."""
        try:
            subprocess.run(["nmcli", "device", "wifi", "connect", ssid], capture_output=True, text=True, timeout=30)
            return True
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to connect WiFi: %s", e)
            return False

    @staticmethod
    def disconnect_wifi(interface_name: str = "wlan0") -> bool:
        data = daemon_client.call_json("NetworkDisconnectWifi", interface_name)
        if isinstance(data, bool):
            return data
        return NetworkUtils.disconnect_wifi_local(interface_name)

    @staticmethod
    def disconnect_wifi_local(interface_name: str = "wlan0") -> bool:
        """Local fallback for disconnecting Wi-Fi interface."""
        try:
            subprocess.run(["nmcli", "device", "disconnect", interface_name], capture_output=True, text=True, timeout=20)
            return True
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to disconnect WiFi: %s", e)
            return False

    @staticmethod
    def apply_dns(connection_name: str, dns_servers: str) -> bool:
        data = daemon_client.call_json("NetworkApplyDns", connection_name, dns_servers)
        if isinstance(data, bool):
            return data
        return NetworkUtils.apply_dns_local(connection_name, dns_servers)

    @staticmethod
    def apply_dns_local(connection_name: str, dns_servers: str) -> bool:
        """Local fallback for applying DNS profile to a connection."""
        try:
            if dns_servers == "auto":
                cmd = [
                    "nmcli",
                    "con",
                    "mod",
                    connection_name,
                    "ipv4.ignore-auto-dns",
                    "no",
                    "ipv6.ignore-auto-dns",
                    "no",
                    "ipv4.dns",
                    "",
                ]
            else:
                cmd = [
                    "nmcli",
                    "con",
                    "mod",
                    connection_name,
                    "ipv4.dns",
                    dns_servers,
                    "ipv4.ignore-auto-dns",
                    "yes",
                ]
            subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            return True
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to apply DNS: %s", e)
            return False

    @staticmethod
    def set_hostname_privacy(connection_name: str, hide: bool) -> bool:
        data = daemon_client.call_json("NetworkSetHostnamePrivacy", connection_name, bool(hide))
        if isinstance(data, bool):
            return data
        return NetworkUtils.set_hostname_privacy_local(connection_name, hide)

    @staticmethod
    def set_hostname_privacy_local(connection_name: str, hide: bool) -> bool:
        """Local fallback for setting DHCP hostname privacy."""
        try:
            value = "no" if hide else "yes"
            subprocess.run(
                ["nmcli", "connection", "modify", connection_name, "ipv4.dhcp-send-hostname", value],
                capture_output=True,
                text=True,
                timeout=20,
            )
            return True
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("Failed to set hostname privacy: %s", e)
            return False
