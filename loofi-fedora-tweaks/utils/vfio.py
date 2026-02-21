"""Backward-compat shim — use services.virtualization instead."""
import warnings
warnings.warn(
    "utils.vfio is deprecated. Import from services.virtualization instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.virtualization.vfio import VFIOAssistant  # noqa: F401, E402
