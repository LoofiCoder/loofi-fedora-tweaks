"""Backward-compat shim — use services.security instead."""
import warnings
warnings.warn(
    "utils.safety is deprecated. Import from services.security instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.security.safety import SafetyManager  # noqa: F401, E402
