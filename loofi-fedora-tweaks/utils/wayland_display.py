"""Backward-compatibility shim - use `services.desktop` instead."""
import warnings

warnings.warn(
    "utils.wayland_display is deprecated. Import from services.desktop instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.desktop.display import DisplayInfo, WaylandDisplayManager  # noqa: F401, E402
