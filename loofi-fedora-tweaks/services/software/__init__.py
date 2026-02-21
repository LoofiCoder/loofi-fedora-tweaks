"""
Software Services Layer — v2.0.0 "Evolution"

Centralized software management for:
- Flatpak analysis and cleanup (flatpak.py)
"""

from services.software.flatpak import (
    FlatpakAppPermissions,
    FlatpakManager,
    FlatpakPermission,
    FlatpakSizeEntry,
)

__all__ = [
    "FlatpakAppPermissions",
    "FlatpakManager",
    "FlatpakPermission",
    "FlatpakSizeEntry",
]
