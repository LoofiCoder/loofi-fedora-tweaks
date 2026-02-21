"""Backward-compat shim — use services.security instead."""
import warnings
warnings.warn(
    "utils.audit is deprecated. Import from services.security instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.security.audit import AuditLogger  # noqa: F401, E402
