"""core.ai — AI/ML features: Ollama, llama.cpp, model management, RAG indexing."""

from core.ai.ai import AIConfigManager, LlamaCppManager, OllamaManager, Result  # noqa: F401
from core.ai.ai_models import (  # noqa: F401
    AIModelManager,
    RECOMMENDED_MODELS,
    _PARAM_BASE_MB,
    _QUANT_RAM_MULTIPLIERS,
)
from core.ai.context_rag import ContextRAGManager  # noqa: F401

__all__ = [
    "AIConfigManager",
    "AIModelManager",
    "ContextRAGManager",
    "LlamaCppManager",
    "OllamaManager",
    "RECOMMENDED_MODELS",
    "Result",
    "_PARAM_BASE_MB",
    "_QUANT_RAM_MULTIPLIERS",
]
