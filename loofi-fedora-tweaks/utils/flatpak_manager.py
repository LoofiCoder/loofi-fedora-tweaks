"""
Deprecated — use ``services.software`` instead.

This module is a backward-compatibility shim that re-exports from
``services.software.flatpak``. It will be removed in a future version.
"""

import warnings

warnings.warn(
    "utils.flatpak_manager is deprecated. Import from services.software instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.software.flatpak import (  # noqa: F401, E402
    FlatpakAppPermissions,
    FlatpakManager,
    FlatpakPermission,
    FlatpakSizeEntry,
)
