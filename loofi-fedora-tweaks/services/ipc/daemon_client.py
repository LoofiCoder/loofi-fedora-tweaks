"""D-Bus daemon IPC client."""

from __future__ import annotations

import json
import os
from typing import Any

from utils.log import get_logger

from daemon.interfaces import BUS_NAME, INTERFACE, OBJECT_PATH
from services.ipc.errors import (
    DaemonClientError,
    DaemonExecutionError,
    DaemonRequiredModeError,
    DaemonUnavailableError,
    DaemonValidationError,
)
from services.ipc.types import DaemonError, DaemonResponse, is_package_payload, is_system_payload

logger = get_logger(__name__)

try:
    import dbus  # type: ignore[import-not-found]
except ImportError:
    dbus = None  # type: ignore[assignment]

_DBUS_EXCEPTIONS: tuple[type[BaseException], ...] = ()
if dbus is not None and hasattr(dbus, "DBusException"):
    _DBUS_EXCEPTIONS = (dbus.DBusException,)  # type: ignore[attr-defined]


class DaemonClient:
    """Client for Loofi daemon D-Bus methods."""

    MODE_ENV = "LOOFI_IPC_MODE"
    _VALID_MODES = {"disabled", "preferred", "required"}

    def __init__(self, timeout: int = 8) -> None:
        self.timeout = timeout

    @classmethod
    def get_mode(cls) -> str:
        """Get IPC mode from environment."""
        mode = os.getenv(cls.MODE_ENV, "preferred").strip().lower()
        return mode if mode in cls._VALID_MODES else "preferred"

    def call_json(self, method: str, *args: Any) -> Any | None:
        """Call a daemon method and return parsed data.

        Returns None when mode is disabled or in preferred mode on transport failure.
        In required mode, transport failures raise DaemonRequiredModeError.
        """
        mode = self.get_mode()
        if mode == "disabled":
            return None

        try:
            payload = self._call_raw(method, *args)
            response = self._parse(payload)
            if response.ok:
                self._validate_payload(method, response.data)
                return response.data
            self._raise_domain_error(response.error)
        except (DaemonValidationError, DaemonExecutionError):
            raise
        except DaemonClientError as exc:
            if mode == "required":
                raise DaemonRequiredModeError(str(exc)) from exc
            logger.debug("Falling back to local mode after daemon error: %s", exc)
            return None
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError) as exc:
            if mode == "required":
                raise DaemonRequiredModeError(str(exc)) from exc
            logger.debug("Falling back to local mode after daemon error: %s", exc)
            return None

        return None

    def _call_raw(self, method: str, *args: Any) -> str:
        if dbus is None:
            raise DaemonUnavailableError("dbus-python not available")

        try:
            bus = dbus.SessionBus()
            proxy = bus.get_object(BUS_NAME, OBJECT_PATH)
            func = proxy.get_dbus_method(method, INTERFACE)
            result = func(*args, timeout=self.timeout)
            return str(result)
        except _DBUS_EXCEPTIONS as exc:
            raise DaemonUnavailableError(f"D-Bus call failed: {exc}") from exc
        except (OSError, RuntimeError, ValueError, TypeError, AttributeError) as exc:
            raise DaemonUnavailableError(f"D-Bus call failed: {exc}") from exc

    @staticmethod
    def _parse(payload: str) -> DaemonResponse:
        try:
            raw = json.loads(payload)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise DaemonClientError(f"Invalid daemon response: {exc}") from exc

        if not isinstance(raw, dict):
            raise DaemonClientError("Invalid daemon response: envelope must be an object")

        ok_value = raw.get("ok")
        if not isinstance(ok_value, bool):
            raise DaemonClientError("Invalid daemon response: 'ok' must be a boolean")

        error = raw.get("error")
        parsed_error = None
        if error is not None and not isinstance(error, dict):
            raise DaemonClientError("Invalid daemon response: 'error' must be an object or null")

        if isinstance(error, dict):
            parsed_error = DaemonError(
                code=str(error.get("code", "unknown")),
                message=str(error.get("message", "Unknown daemon error")),
            )

        return DaemonResponse(ok=ok_value, data=raw.get("data"), error=parsed_error)

    @staticmethod
    def _raise_domain_error(error: DaemonError | None) -> None:
        if error is None:
            raise DaemonExecutionError("Daemon returned error without payload")
        if error.code == "validation_error":
            raise DaemonValidationError(error.message)
        raise DaemonExecutionError(error.message)

    @staticmethod
    def _validate_payload(method: str, payload: Any) -> None:
        if not is_package_payload(method, payload):
            raise DaemonClientError(f"Invalid daemon response for {method}: malformed payload")
        if not is_system_payload(method, payload):
            raise DaemonClientError(f"Invalid daemon response for {method}: malformed payload")


daemon_client = DaemonClient()
