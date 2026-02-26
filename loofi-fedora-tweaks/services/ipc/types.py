"""IPC transport type contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DaemonError:
    """Error payload returned by daemon service."""

    code: str
    message: str


@dataclass(frozen=True)
class DaemonResponse:
    """Parsed daemon response envelope."""

    ok: bool
    data: Any = None
    error: DaemonError | None = None


def is_action_result_payload(payload: Any) -> bool:
    """Return True when payload resembles ActionResult serialized dictionary."""
    if not isinstance(payload, dict):
        return False
    success = payload.get("success")
    message = payload.get("message")
    return isinstance(success, bool) and isinstance(message, str)


def is_package_payload(method: str, payload: Any) -> bool:
    """Validate daemon payload shape for package-related IPC methods."""
    if method in {
        "PackageInstall",
        "PackageRemove",
        "PackageUpdate",
        "PackageSearch",
        "PackageInfo",
        "PackageListInstalled",
    }:
        return is_action_result_payload(payload)

    if method == "PackageIsInstalled":
        return isinstance(payload, bool)

    if method.startswith("Package"):
        return False

    return True


def is_system_payload(method: str, payload: Any) -> bool:
    """Validate daemon payload shape for system-related IPC methods."""
    if method in {
        "SystemReboot",
        "SystemShutdown",
        "SystemSuspend",
        "SystemUpdateGrub",
        "SystemSetHostname",
    }:
        return is_action_result_payload(payload)

    if method == "SystemHasPendingReboot":
        return isinstance(payload, bool)

    if method in {"SystemGetPackageManager", "SystemGetVariantName"}:
        return isinstance(payload, str)

    if method.startswith("System"):
        return False

    return True
