"""Backward-compat shim — use services.network instead."""
import warnings
warnings.warn(
    "utils.mesh_discovery is deprecated. Import from services.network instead.",
    DeprecationWarning,
    stacklevel=2,
)
from services.network.mesh import MeshDiscovery, PeerDevice  # noqa: F401, E402
