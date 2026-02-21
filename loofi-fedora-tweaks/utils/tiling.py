"""Backward-compatibility shim - use `services.desktop` instead."""
import warnings

warnings.warn(
    "utils.tiling is deprecated. Import from services.desktop instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.desktop.tiling import DotfileManager, TilingManager, Result  # noqa: F401, E402
