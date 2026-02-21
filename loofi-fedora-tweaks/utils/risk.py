"""Backward-compat shim — use services.security instead."""
import warnings
warnings.warn(
    "utils.risk is deprecated. Import from services.security instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.security.risk import RiskEntry, RiskLevel, RiskRegistry  # noqa: F401, E402
