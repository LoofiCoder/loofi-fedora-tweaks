"""Input validators for daemon operations."""

from __future__ import annotations

import ast
from pathlib import Path
import re
import xml.etree.ElementTree as ET


_CONNECTION_RE = re.compile(r"^[A-Za-z0-9_.:@\-\s]{1,128}$")
_ZONE_RE = re.compile(r"^[A-Za-z0-9_.\-]{0,64}$")
_PORT_RE = re.compile(r"^\d{1,5}(-\d{1,5})?$")
_INTERFACE_RE = re.compile(r"^[A-Za-z0-9_.:@\-]{1,32}$")
_FIREWALL_SERVICE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,63}$")
_UNIT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9@_.\-]{0,127}$")
_PACKAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.:@\-]{0,127}$")
_HOSTNAME_RE = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?(?:\.(?!-)[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?)*$")
_DNS_RE = re.compile(r"^[A-Za-z0-9:.\-,\s]{1,256}$")
_PROTOCOLS = {"tcp", "udp"}
_UNIT_SCOPES = {"user", "system"}
_UNIT_FILTERS = {"all", "gaming", "failed", "active"}


class ValidationError(ValueError):
    """Raised when daemon input validation fails."""


def validate_connection_name(value: str) -> str:
    """Validate NetworkManager connection name."""
    raw = (value or "").strip()
    if not raw or not _CONNECTION_RE.fullmatch(raw):
        raise ValidationError("Invalid connection name")
    return raw


def validate_zone(value: str) -> str:
    """Validate firewalld zone input."""
    raw = (value or "").strip()
    if not _ZONE_RE.fullmatch(raw):
        raise ValidationError("Invalid firewall zone")
    return raw


def validate_port(value: str) -> str:
    """Validate a firewall port string (single port or range)."""
    raw = (value or "").strip()
    if not _PORT_RE.fullmatch(raw):
        raise ValidationError("Invalid port value")
    if "-" in raw:
        start, end = raw.split("-", 1)
        if not _is_valid_port(start) or not _is_valid_port(end) or int(start) > int(end):
            raise ValidationError("Invalid port range")
        return raw
    if not _is_valid_port(raw):
        raise ValidationError("Invalid port")
    return raw


def validate_protocol(value: str) -> str:
    """Validate network protocol."""
    raw = (value or "").strip().lower()
    if raw not in _PROTOCOLS:
        raise ValidationError("Invalid protocol")
    return raw


def validate_boolean(value: object, field_name: str) -> bool:
    """Validate a strict boolean input."""
    if not isinstance(value, bool):
        raise ValidationError(f"Invalid {field_name}")
    return value


def validate_ssid(value: str) -> str:
    """Validate Wi-Fi SSID input."""
    raw = str(value or "").strip()
    if not raw or len(raw) > 64 or any(ord(ch) < 32 for ch in raw):
        raise ValidationError("Invalid SSID")
    return raw


def validate_interface_name(value: str) -> str:
    """Validate network interface name."""
    raw = str(value or "wlan0").strip()
    if not _INTERFACE_RE.fullmatch(raw):
        raise ValidationError("Invalid interface name")
    return raw


def validate_dns_servers(value: str) -> str:
    """Validate DNS server specification string."""
    raw = str(value or "").strip()
    if raw == "auto":
        return raw
    if not raw or not _DNS_RE.fullmatch(raw):
        raise ValidationError("Invalid DNS servers")
    return raw


def validate_firewall_service(value: str) -> str:
    """Validate firewalld service identifier."""
    raw = str(value or "").strip().lower()
    if not _FIREWALL_SERVICE_RE.fullmatch(raw):
        raise ValidationError("Invalid firewall service")
    return raw


def validate_rich_rule(value: str) -> str:
    """Validate firewalld rich rule string."""
    raw = str(value or "").strip()
    if not raw or len(raw) > 512 or "\n" in raw or "\r" in raw:
        raise ValidationError("Invalid rich rule")
    return raw


def validate_unit_scope(value: str) -> str:
    """Validate systemd unit scope."""
    raw = str(value or "").strip().lower()
    if raw not in _UNIT_SCOPES:
        raise ValidationError("Invalid unit scope")
    return raw


def validate_unit_filter(value: str) -> str:
    """Validate list-units filter selector."""
    raw = str(value or "").strip().lower()
    if raw not in _UNIT_FILTERS:
        raise ValidationError("Invalid unit filter")
    return raw


def validate_unit_name(value: str) -> str:
    """Validate a systemd unit name without suffix."""
    raw = str(value or "").strip()
    if raw.endswith(".service"):
        raw = raw[:-8]
    if not _UNIT_NAME_RE.fullmatch(raw):
        raise ValidationError("Invalid unit name")
    return raw


def validate_delay_seconds(value: object) -> int:
    """Validate reboot/shutdown delay seconds."""
    if isinstance(value, bool):
        raise ValidationError("Invalid delay seconds")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError:
            raise ValidationError("Invalid delay seconds")
    else:
        raise ValidationError("Invalid delay seconds")
    if parsed < 0 or parsed > 86400:
        raise ValidationError("Invalid delay seconds")
    return parsed


def validate_hostname(value: str) -> str:
    """Validate hostname input."""
    raw = str(value or "").strip()
    if not _HOSTNAME_RE.fullmatch(raw):
        raise ValidationError("Invalid hostname")
    return raw


def validate_description(value: str, field_name: str = "description") -> str:
    """Validate optional descriptive text inputs."""
    raw = str(value or "").strip()
    if len(raw) > 256 or any(ord(ch) < 32 and ch not in {9} for ch in raw):
        raise ValidationError(f"Invalid {field_name}")
    return raw


def validate_package_name(value: str) -> str:
    """Validate package identifier used for package operations."""
    raw = str(value or "").strip()
    if not _PACKAGE_RE.fullmatch(raw):
        raise ValidationError("Invalid package")
    return raw


def validate_package_list(value: object) -> list[str]:
    """Validate package list payload for package actions."""
    if not isinstance(value, list):
        raise ValidationError("Invalid package list")
    cleaned = [validate_package_name(pkg) for pkg in value]
    if not cleaned:
        raise ValidationError("Invalid package list")
    return cleaned


def validate_search_query(value: str) -> str:
    """Validate package search query input."""
    raw = str(value or "").strip()
    if not raw or len(raw) > 128 or "\n" in raw or "\r" in raw:
        raise ValidationError("Invalid search query")
    return raw


def validate_search_limit(value: object) -> int:
    """Validate package search result limit."""
    if isinstance(value, bool):
        raise ValidationError("Invalid search limit")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError:
            raise ValidationError("Invalid search limit")
    else:
        raise ValidationError("Invalid search limit")
    if parsed < 1 or parsed > 200:
        raise ValidationError("Invalid search limit")
    return parsed


def _is_valid_port(value: str) -> bool:
    try:
        port = int(value)
    except (TypeError, ValueError):
        return False
    return 1 <= port <= 65535


def build_policy_inventory(policy_dir: str | Path | None = None) -> list[dict[str, str]]:
    """Build a policy action inventory from Polkit policy files."""
    base_dir = _resolve_policy_dir(policy_dir)
    entries: list[dict[str, str]] = []

    for policy_path in sorted(base_dir.glob("org.loofi.fedora-tweaks*.policy")):
        entries.extend(_extract_policy_actions(policy_path))

    return sorted(entries, key=lambda item: item["action_id"])


def _resolve_policy_dir(policy_dir: str | Path | None) -> Path:
    if policy_dir is None:
        return Path(__file__).resolve().parents[1] / "config"
    return Path(policy_dir)


def _extract_policy_actions(policy_path: Path) -> list[dict[str, str]]:
    try:
        # Polkit policy files are local project assets under config/.
        root = ET.parse(policy_path).getroot()  # nosec B314
    except ET.ParseError:
        return []

    actions: list[dict[str, str]] = []
    for action in root.findall("action"):
        action_id = (action.get("id") or "").strip()
        if not action_id.startswith("org.loofi.fedora-tweaks"):
            continue

        defaults = action.find("defaults")
        actions.append(
            {
                "action_id": action_id,
                "description": (action.findtext("description") or "").strip(),
                "message": (action.findtext("message") or "").strip(),
                "allow_any": _get_default(defaults, "allow_any"),
                "allow_inactive": _get_default(defaults, "allow_inactive"),
                "allow_active": _get_default(defaults, "allow_active"),
                "policy_file": policy_path.name,
            }
        )

    return actions


def _get_default(defaults: ET.Element | None, field_name: str) -> str:
    if defaults is None:
        return ""
    return (defaults.findtext(field_name) or "").strip()


def build_validator_coverage_map(handler_dir: str | Path | None = None) -> list[dict[str, object]]:
    """Map daemon handler methods to validator coverage and gaps."""
    base_dir = _resolve_handler_dir(handler_dir)
    coverage: list[dict[str, object]] = []

    for handler_path in sorted(base_dir.glob("*_handler.py")):
        coverage.extend(_extract_handler_method_coverage(handler_path))

    return sorted(coverage, key=lambda item: (str(item["handler"]), str(item["method"])))


def _resolve_handler_dir(handler_dir: str | Path | None) -> Path:
    if handler_dir is None:
        return Path(__file__).resolve().parent / "handlers"
    return Path(handler_dir)


def _extract_handler_method_coverage(handler_path: Path) -> list[dict[str, object]]:
    tree = ast.parse(handler_path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or not node.name.endswith("Handler"):
            continue

        for method in node.body:
            if not isinstance(method, ast.FunctionDef) or method.name.startswith("_"):
                continue
            if not _is_staticmethod(method):
                continue

            parameters = [arg.arg for arg in method.args.args]
            validator_calls, validated_parameters = _collect_validators(method)
            unvalidated_parameters = [p for p in parameters if p not in validated_parameters]

            rows.append(
                {
                    "handler": node.name,
                    "method": method.name,
                    "parameters": parameters,
                    "validator_calls": sorted(validator_calls),
                    "validated_parameters": sorted(validated_parameters),
                    "unvalidated_parameters": sorted(unvalidated_parameters),
                }
            )

    return rows


def _is_staticmethod(method: ast.FunctionDef) -> bool:
    for decorator in method.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == "staticmethod":
            return True
    return False


def _collect_validators(method: ast.FunctionDef) -> tuple[set[str], set[str]]:
    validators: set[str] = set()
    params: set[str] = set()

    for node in ast.walk(method):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if not node.func.id.startswith("validate_"):
            continue

        validators.add(node.func.id)
        for argument in node.args:
            if isinstance(argument, ast.Name):
                params.add(argument.id)

    return validators, params
