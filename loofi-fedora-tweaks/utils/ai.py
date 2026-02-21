"""Backward-compatibility shim. Use core.ai.ai instead."""
from core.ai.ai import *  # noqa: F401, F403
from core.ai.ai import AIConfigManager, LlamaCppManager, OllamaManager, Result  # noqa: F401
