"""Backward-compatibility shim - use `services.desktop` instead."""
import warnings

warnings.warn(
    "utils.kwin_tiling is deprecated. Import from services.desktop instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.desktop.kwin import KWinManager, Result  # noqa: F401, E402
