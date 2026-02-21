"""Backward-compatibility shim — use ``services.desktop`` instead."""

import warnings

warnings.warn(
    "utils.desktop_utils is deprecated. Import from services.desktop instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.desktop.desktop import DesktopUtils  # noqa: F401, E402
