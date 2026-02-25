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
