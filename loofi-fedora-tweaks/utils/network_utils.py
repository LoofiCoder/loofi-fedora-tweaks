"""Backward-compat shim — use services.network instead."""
import warnings
warnings.warn(
    "utils.network_utils is deprecated. Import from services.network instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.network.network import NetworkUtils  # noqa: F401, E402
