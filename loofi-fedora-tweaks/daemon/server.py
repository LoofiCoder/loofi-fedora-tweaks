"""D-Bus service host for Loofi daemon."""

from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

from daemon.contracts import error_response, ok_response
from daemon.handlers import FirewallHandler, NetworkHandler
from daemon.interfaces import INTERFACE, OBJECT_PATH
from daemon.validators import ValidationError

logger = logging.getLogger(__name__)

try:
    import dbus  # type: ignore[import-not-found]
    import dbus.service  # type: ignore[import-not-found]
except ImportError:
    dbus = None  # type: ignore[assignment]


_ServiceMethod = TypeVar("_ServiceMethod", bound=Callable[..., Any])


class DaemonServiceBase:
    """Base class for fallback behavior when dbus is missing."""

    def Ping(self) -> str:  # noqa: N802
        return ok_response("pong")


def _no_op_method(*_args: Any, **_kwargs: Any) -> Callable[[_ServiceMethod], _ServiceMethod]:
    """Return a decorator compatible with dbus.service.method when dbus is unavailable."""

    def _decorator(func: _ServiceMethod) -> _ServiceMethod:
        return func

    return _decorator


_DbusObjectBase: type[Any]

if dbus is None:
    _DbusObjectBase = DaemonServiceBase
    _dbus_method = _no_op_method
else:
    _DbusObjectBase = dbus.service.Object
    _dbus_method = dbus.service.method


class DaemonService(_DbusObjectBase):  # type: ignore[misc,valid-type]
    """D-Bus object exposing daemon methods."""

    def __init__(self, bus_name: Any = None):
        if dbus is None:
            DaemonServiceBase.__init__(self)
            return
        if bus_name is None:
            raise ValueError("bus_name is required when dbus is available")
        dbus.service.Object.__init__(self, bus_name, OBJECT_PATH)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def Ping(self) -> str:  # noqa: N802
        return ok_response("pong")

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def GetCapabilities(self) -> str:  # noqa: N802
        return ok_response(
            {
                "version": 1,
                "network": [
                    "scan_wifi",
                    "load_vpn_connections",
                    "detect_current_dns",
                    "get_active_connection",
                    "check_hostname_privacy",
                    "reactivate_connection",
                    "connect_wifi",
                    "disconnect_wifi",
                    "apply_dns",
                    "set_hostname_privacy",
                ],
                "firewall": [
                    "get_status",
                    "list_ports",
                    "list_services",
                    "get_default_zone",
                    "get_zones",
                    "get_active_zones",
                    "list_rich_rules",
                    "set_default_zone",
                    "add_service",
                    "remove_service",
                    "add_rich_rule",
                    "remove_rich_rule",
                    "open_port",
                    "close_port",
                    "start_firewall",
                    "stop_firewall",
                ],
                "ports": ["scan_ports", "security_score"],
            }
        )

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def NetworkScanWifi(self) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.scan_wifi)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def NetworkLoadVpnConnections(self) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.load_vpn_connections)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def NetworkDetectCurrentDns(self) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.detect_current_dns)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def NetworkGetActiveConnection(self) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.get_active_connection)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def NetworkCheckHostnamePrivacy(self, connection_name: str) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.check_hostname_privacy, connection_name)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def NetworkReactivateConnection(self, connection_name: str) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.reactivate_connection, connection_name)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def NetworkConnectWifi(self, ssid: str) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.connect_wifi, ssid)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def NetworkDisconnectWifi(self, interface_name: str) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.disconnect_wifi, interface_name)

    @_dbus_method(INTERFACE, in_signature="ss", out_signature="s")
    def NetworkApplyDns(self, connection_name: str, dns_servers: str) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.apply_dns, connection_name, dns_servers)

    @_dbus_method(INTERFACE, in_signature="sb", out_signature="s")
    def NetworkSetHostnamePrivacy(self, connection_name: str, hide: bool) -> str:  # noqa: N802
        return self._safe_call(NetworkHandler.set_hostname_privacy, connection_name, hide)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def FirewallGetStatus(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.get_status)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def FirewallListPorts(self, zone: str = "") -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.list_ports, zone)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def FirewallListServices(self, zone: str = "") -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.list_services, zone)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def FirewallGetDefaultZone(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.get_default_zone)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def FirewallGetZones(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.get_zones)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def FirewallGetActiveZones(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.get_active_zones)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def FirewallListRichRules(self, zone: str = "") -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.list_rich_rules, zone)

    @_dbus_method(INTERFACE, in_signature="s", out_signature="s")
    def FirewallSetDefaultZone(self, zone: str) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.set_default_zone, zone)

    @_dbus_method(INTERFACE, in_signature="ssb", out_signature="s")
    def FirewallAddService(self, service: str, zone: str, permanent: bool) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.add_service, service, zone, permanent)

    @_dbus_method(INTERFACE, in_signature="ssb", out_signature="s")
    def FirewallRemoveService(self, service: str, zone: str, permanent: bool) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.remove_service, service, zone, permanent)

    @_dbus_method(INTERFACE, in_signature="ssb", out_signature="s")
    def FirewallAddRichRule(self, rule: str, zone: str, permanent: bool) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.add_rich_rule, rule, zone, permanent)

    @_dbus_method(INTERFACE, in_signature="ssb", out_signature="s")
    def FirewallRemoveRichRule(self, rule: str, zone: str, permanent: bool) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.remove_rich_rule, rule, zone, permanent)

    @_dbus_method(INTERFACE, in_signature="sssb", out_signature="s")
    def FirewallOpenPort(self, port: str, protocol: str, zone: str, permanent: bool) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.open_port, port, protocol, zone, permanent)

    @_dbus_method(INTERFACE, in_signature="sssb", out_signature="s")
    def FirewallClosePort(self, port: str, protocol: str, zone: str, permanent: bool) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.close_port, port, protocol, zone, permanent)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def FirewallStart(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.start_firewall)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def FirewallStop(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.stop_firewall)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def PortAuditScan(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.scan_ports)

    @_dbus_method(INTERFACE, in_signature="", out_signature="s")
    def PortAuditSecurityScore(self) -> str:  # noqa: N802
        return self._safe_call(FirewallHandler.security_score)

    @staticmethod
    def _safe_call(func: Callable[..., Any], *args: Any) -> str:
        try:
            return ok_response(func(*args))
        except ValidationError as exc:
            return error_response("validation_error", str(exc))
        except (OSError, RuntimeError, ValueError, TypeError) as exc:
            logger.exception("Daemon method failure")
            return error_response("execution_error", str(exc))
