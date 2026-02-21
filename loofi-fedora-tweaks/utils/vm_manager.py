"""Backward-compat shim — use services.virtualization instead."""
import warnings
warnings.warn(
    "utils.vm_manager is deprecated. Import from services.virtualization instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.virtualization.vm_manager import VM_FLAVORS, VMInfo, VMManager  # noqa: F401, E402
