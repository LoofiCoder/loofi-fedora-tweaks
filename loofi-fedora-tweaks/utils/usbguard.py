"""Backward-compat shim — use services.security instead."""
import warnings
warnings.warn(
    "utils.usbguard is deprecated. Import from services.security instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.security.usbguard import USBDevice, USBGuardManager  # noqa: F401, E402

# Keep backward-compat Result alias
from services.security.usbguard import Result  # noqa: F401, E402
