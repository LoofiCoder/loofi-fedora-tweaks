"""Backward-compat shim — use services.security instead."""
import warnings
warnings.warn(
    "utils.firewall_manager is deprecated. Import from services.security instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.security.firewall import FirewallInfo, FirewallManager, FirewallResult  # noqa: F401, E402
