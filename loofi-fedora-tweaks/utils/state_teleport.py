"""Backward-compatibility shim - use `services.storage` instead."""
import warnings

warnings.warn(
    "utils.state_teleport is deprecated. Import from services.storage instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.storage.teleport import StateTeleportManager  # noqa: F401, E402
