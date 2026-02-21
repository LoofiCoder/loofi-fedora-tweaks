"""Backward-compatibility shim. Use core.ai.ai_models instead."""
from core.ai.ai_models import *  # noqa: F401, F403
from core.ai.ai_models import AIModelManager, RECOMMENDED_MODELS, Result, _PARAM_BASE_MB, _QUANT_RAM_MULTIPLIERS  # noqa: F401
