"""Shared daemon response contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ErrorPayload:
    """Error payload returned by daemon methods."""

    code: str
    message: str


@dataclass(frozen=True)
class ResponseEnvelope:
    """Standardized daemon response envelope."""

    ok: bool
    data: Any = None
    error: Optional[ErrorPayload] = None

    def to_json(self) -> str:
        """Serialize envelope to JSON string."""
        payload = {
            "ok": self.ok,
            "data": self.data,
            "error": None if self.error is None else {"code": self.error.code, "message": self.error.message},
        }
        return json.dumps(payload, default=str)


def ok_response(data: Any = None) -> str:
    """Build a successful response envelope."""
    return ResponseEnvelope(ok=True, data=data, error=None).to_json()


def error_response(code: str, message: str) -> str:
    """Build an error response envelope."""
    return ResponseEnvelope(ok=False, data=None, error=ErrorPayload(code=code, message=message)).to_json()
