"""Network-related daemon handlers."""

from __future__ import annotations

from services.network.network import NetworkUtils

from daemon.validators import validate_boolean, validate_connection_name, validate_dns_servers, validate_interface_name, validate_ssid


class NetworkHandler:
    """Serve network operations for IPC callers."""

    @staticmethod
    def scan_wifi() -> list[dict[str, str]]:
        rows = NetworkUtils.scan_wifi_local()
        return [
            {"ssid": ssid, "signal": signal, "security": security, "active": active}
            for ssid, signal, security, active in rows
        ]

    @staticmethod
    def load_vpn_connections() -> list[dict[str, str]]:
        rows = NetworkUtils.load_vpn_connections_local()
        return [{"name": name, "type": conn_type, "status": status} for name, conn_type, status in rows]

    @staticmethod
    def detect_current_dns() -> str:
        return NetworkUtils.detect_current_dns_local()

    @staticmethod
    def get_active_connection() -> str:
        return NetworkUtils.get_active_connection_local() or ""

    @staticmethod
    def check_hostname_privacy(connection_name: str) -> bool:
        valid_name = validate_connection_name(connection_name)
        result = NetworkUtils.check_hostname_privacy_local(valid_name)
        return bool(result)

    @staticmethod
    def reactivate_connection(connection_name: str) -> bool:
        valid_name = validate_connection_name(connection_name)
        return NetworkUtils.reactivate_connection_local(valid_name)

    @staticmethod
    def connect_wifi(ssid: str) -> bool:
        valid_ssid = validate_ssid(ssid)
        return NetworkUtils.connect_wifi_local(valid_ssid)

    @staticmethod
    def disconnect_wifi(interface_name: str = "wlan0") -> bool:
        valid_interface_name = validate_interface_name(interface_name)
        return NetworkUtils.disconnect_wifi_local(valid_interface_name)

    @staticmethod
    def apply_dns(connection_name: str, dns_servers: str) -> bool:
        valid_name = validate_connection_name(connection_name)
        valid_dns_servers = validate_dns_servers(dns_servers)
        return NetworkUtils.apply_dns_local(valid_name, valid_dns_servers)

    @staticmethod
    def set_hostname_privacy(connection_name: str, hide: bool) -> bool:
        valid_name = validate_connection_name(connection_name)
        valid_hide = validate_boolean(hide, "hide")
        return NetworkUtils.set_hostname_privacy_local(valid_name, valid_hide)
