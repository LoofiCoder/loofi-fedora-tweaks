"""IPC client package for daemon communication."""

from services.ipc.daemon_client import DaemonClient, daemon_client
from services.ipc.errors import (
    DaemonClientError,
    DaemonExecutionError,
    DaemonRequiredModeError,
    DaemonUnavailableError,
    DaemonValidationError,
)

__all__ = [
    "DaemonClient",
    "DaemonClientError",
    "DaemonExecutionError",
    "DaemonRequiredModeError",
    "DaemonUnavailableError",
    "DaemonValidationError",
    "daemon_client",
]
