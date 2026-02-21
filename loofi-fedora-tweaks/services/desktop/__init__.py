"""services.desktop — Desktop environment services.

Re-exports from submodules for convenient top-level access:
    from services.desktop import DesktopUtils, KWinManager, TilingManager, ...
"""

from services.desktop.desktop import DesktopUtils
from services.desktop.display import DisplayInfo, WaylandDisplayManager
from services.desktop.kwin import KWinManager
from services.desktop.kwin import Result as KWinResult
from services.desktop.tiling import DotfileManager, TilingManager
from services.desktop.tiling import Result as TilingResult

__all__ = [
    "DesktopUtils",
    "DisplayInfo",
    "DotfileManager",
    "KWinManager",
    "KWinResult",
    "TilingManager",
    "TilingResult",
    "WaylandDisplayManager",
]
