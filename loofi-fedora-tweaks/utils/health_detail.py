"""Backward-compatibility shim. Use core.diagnostics.health_detail instead."""
from core.diagnostics.health_detail import *  # noqa: F401, F403
from core.diagnostics.health_detail import ComponentScore, HealthDetailManager, HealthFix  # noqa: F401
