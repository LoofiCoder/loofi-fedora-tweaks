"""Backward-compatibility shim - use `services.storage` instead."""
import warnings

warnings.warn(
    "utils.cloud_sync is deprecated. Import from services.storage instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.storage.cloud_sync import CloudSyncManager  # noqa: F401, E402
