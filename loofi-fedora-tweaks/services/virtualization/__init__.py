"""Virtualization services — VM management, VFIO, disposable VMs.

Migrated from utils/ in v2.0.0.
"""

from services.virtualization.disposable_vm import DisposableVMManager
from services.virtualization.vfio import VFIOAssistant
from services.virtualization.virtualization import (
    IOMMUDevice,
    IOMMUGroup,
    VirtStatus,
    VirtualizationManager,
)
from services.virtualization.vm_manager import VM_FLAVORS, VMInfo, VMManager

__all__ = [
    "DisposableVMManager",
    "IOMMUDevice",
    "IOMMUGroup",
    "VFIOAssistant",
    "VirtualizationManager",
    "VirtStatus",
    "VM_FLAVORS",
    "VMInfo",
    "VMManager",
]
