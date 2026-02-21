"""Backward-compat shim — use services.virtualization instead."""
import warnings
warnings.warn(
    "utils.virtualization is deprecated. Import from services.virtualization instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.virtualization.virtualization import (  # noqa: F401, E402
    IOMMUDevice,
    IOMMUGroup,
    VirtualizationManager,
    VirtStatus,
)
