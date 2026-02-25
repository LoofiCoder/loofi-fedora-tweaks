"""Input validators for daemon operations."""

from __future__ import annotations

import re


_CONNECTION_RE = re.compile(r"^[A-Za-z0-9_.:@\-\s]{1,128}$")
_ZONE_RE = re.compile(r"^[A-Za-z0-9_.\-]{0,64}$")
_PORT_RE = re.compile(r"^\d{1,5}(-\d{1,5})?$")
_PROTOCOLS = {"tcp", "udp"}


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


def _is_valid_port(value: str) -> bool:
    try:
        port = int(value)
    except (TypeError, ValueError):
        return False
    return 1 <= port <= 65535
