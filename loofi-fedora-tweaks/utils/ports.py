"""Backward-compat shim — use services.network instead."""
import warnings
warnings.warn(
    "utils.network_monitor is deprecated. Import from services.network instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.network.ports import OpenPort, PortAuditor, Result  # noqa: F401, E402
