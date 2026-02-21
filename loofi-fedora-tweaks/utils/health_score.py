"""Backward-compatibility shim. Use core.diagnostics.health_score instead."""
from core.diagnostics.health_score import *  # noqa: F401, F403
from core.diagnostics.health_score import HealthScore, HealthScoreManager  # noqa: F401
