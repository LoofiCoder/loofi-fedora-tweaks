"""Backward-compat shim — use services.virtualization instead."""
import warnings
warnings.warn(
    "utils.disposable_vm is deprecated. Import from services.virtualization instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.virtualization.disposable_vm import DisposableVMManager  # noqa: F401, E402
