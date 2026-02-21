"""Backward-compat shim — use services.security instead."""
import warnings
warnings.warn(
    "utils.sandbox is deprecated. Import from services.security instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.security.sandbox import BubblewrapManager, PluginIsolationManager, SandboxManager  # noqa: F401, E402

# Keep backward-compat Result alias
from services.security.sandbox import Result  # noqa: F401, E402
