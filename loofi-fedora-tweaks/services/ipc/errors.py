"""IPC client error hierarchy."""

from __future__ import annotations


class DaemonClientError(RuntimeError):
    """Base daemon IPC error."""


class DaemonUnavailableError(DaemonClientError):
    """Raised when daemon is unavailable."""


class DaemonValidationError(DaemonClientError):
    """Raised when daemon rejects parameters."""


class DaemonExecutionError(DaemonClientError):
    """Raised when daemon reports execution failure."""


class DaemonRequiredModeError(DaemonClientError):
    """Raised when IPC mode is required but daemon call cannot complete."""
