"""Backward-compatibility shim. Use core.ai.context_rag instead."""
from core.ai.context_rag import *  # noqa: F401, F403
from core.ai.context_rag import (  # noqa: F401
    ContextRAGManager,
    INDEXABLE_PATHS,
    MAX_FILE_SIZE,
    MAX_INDEX_SIZE,
    _CHUNK_OVERLAP,
    _CHUNK_SIZE,
    _INDEX_DIR_NAME,
    _INDEX_FILENAME,
    _SENSITIVE_FILENAME_KEYWORDS,
)
