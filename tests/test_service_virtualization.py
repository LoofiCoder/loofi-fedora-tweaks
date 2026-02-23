"""Tests for services/virtualization/ modules.

Covers:
- services/virtualization/vm_manager.py — VMManager
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))

from services.virtualization.vm_manager import (
    Result,
    VMInfo,
    VMManager,
    VM_FLAVORS,
)


# ===========================================================================
# VMManager tests
# ===========================================================================

class TestVMManagerAvailability(unittest.TestCase):
    """Test VMManager availability checking."""

    @patch('services.virtualization.vm_manager.cached_which')
    def test_is_available_success(self, mock_which):
        """VMManager detects virtualization tools available."""
        mock_which.side_effect = lambda x: f"/usr/bin/{x}" if x in ["virsh", "qemu-system-x86_64"] else None
        result = VMManager.is_available()
        self.assertTrue(result)

    @patch('services.virtualization.vm_manager.cached_which')
    def test_is_available_virsh_missing(self, mock_which):
        """VMManager detects virsh missing."""
        mock_which.side_effect = lambda x: None if x == "virsh" else f"/usr/bin/{x}"
        result = VMManager.is_available()
        self.assertFalse(result)

    @patch('services.virtualization.vm_manager.cached_which')
    def test_is_available_qemu_missing(self, mock_which):
        """VMManager detects qemu missing."""
        mock_which.side_effect = lambda x: "/usr/bin/virsh" if x == "virsh" else None
        result = VMManager.is_available()
        self.assertFalse(result)


class TestVMManagerFlavors(unittest.TestCase):
    """Test VM flavor presets."""

    def test_get_available_flavors_returns_dict(self):
        """Get available flavors returns flavor dictionary."""
        flavors = VMManager.get_available_flavors()
        self.assertIsInstance(flavors, dict)
        self.assertIn("windows11", flavors)
        self.assertIn("fedora", flavors)
        self.assertIn("ubuntu", flavors)

    def test_flavors_have_required_fields(self):
        """VM flavors have required configuration fields."""
        for key, flavor in VM_FLAVORS.items():
            self.assertIn("ram_mb", flavor)
            self.assertIn("vcpus", flavor)
            self.assertIn("disk_gb", flavor)
            self.assertIn("os_variant", flavor)


class TestVMManagerListVMs(unittest.TestCase):
    """Test VM listing."""

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_list_vms_success(self, mock_which, mock_run):
        """List VMs parses virsh output correctly."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(
            stdout=" Id   Name           State\n"
                   "-----------------------------\n"
                   " 1    testvm1        running\n"
                   " -    testvm2        shut off\n",
            returncode=0
        )
        result = VMManager.list_vms()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "testvm1")
        self.assertEqual(result[0].state, "running")
        self.assertEqual(result[1].name, "testvm2")
        self.assertEqual(result[1].state, "shut off")

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_list_vms_empty(self, mock_which, mock_run):
        """List VMs returns empty list when no VMs."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(
            stdout=" Id   Name           State\n"
                   "-----------------------------\n",
            returncode=0
        )
        result = VMManager.list_vms()
        self.assertEqual(result, [])

    @patch('services.virtualization.vm_manager.cached_which')
    def test_list_vms_virsh_not_available(self, mock_which):
        """List VMs returns empty when virsh not available."""
        mock_which.return_value = None
        result = VMManager.list_vms()
        self.assertEqual(result, [])

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_list_vms_timeout(self, mock_which, mock_run):
        """List VMs handles timeout."""
        import subprocess
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.side_effect = subprocess.TimeoutExpired("virsh", 15)
        result = VMManager.list_vms()
        self.assertEqual(result, [])


class TestVMManagerVMInfo(unittest.TestCase):
    """Test VM information retrieval."""

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_get_vm_info_success(self, mock_which, mock_run):
        """Get VM info parses dominfo output."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(
            stdout="State:              running\n"
                   "UUID:               abc-123\n"
                   "Max memory:         4194304 KiB\n"
                   "CPU(s):             4\n",
            returncode=0
        )
        result = VMManager.get_vm_info("testvm")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "testvm")
        self.assertEqual(result.state, "running")
        self.assertEqual(result.uuid, "abc-123")
        self.assertEqual(result.memory_mb, 4096)
        self.assertEqual(result.vcpus, 4)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_get_vm_info_not_found(self, mock_which, mock_run):
        """Get VM info returns None for non-existent VM."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=1)
        result = VMManager.get_vm_info("nonexistent")
        self.assertIsNone(result)

    @patch('services.virtualization.vm_manager.cached_which')
    def test_get_vm_info_virsh_not_available(self, mock_which):
        """Get VM info returns None when virsh not available."""
        mock_which.return_value = None
        result = VMManager.get_vm_info("testvm")
        self.assertIsNone(result)

    @patch('services.virtualization.vm_manager.VMManager.get_vm_info')
    def test_get_vm_state_success(self, mock_info):
        """Get VM state returns state string."""
        mock_info.return_value = VMInfo(name="testvm", state="running")
        result = VMManager.get_vm_state("testvm")
        self.assertEqual(result, "running")

    @patch('services.virtualization.vm_manager.VMManager.get_vm_info')
    def test_get_vm_state_not_found(self, mock_info):
        """Get VM state returns unknown for missing VM."""
        mock_info.return_value = None
        result = VMManager.get_vm_state("testvm")
        self.assertEqual(result, "unknown")


class TestVMManagerCreateVM(unittest.TestCase):
    """Test VM creation."""

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.os.path.isfile')
    @patch('services.virtualization.vm_manager.cached_which')
    @patch('services.virtualization.vm_manager.VMManager.get_default_storage_pool')
    def test_create_vm_success(self, mock_pool, mock_which, mock_isfile, mock_run):
        """Create VM succeeds with valid parameters."""
        mock_pool.return_value = "/var/lib/libvirt/images"
        mock_which.return_value = "/usr/bin/virt-install"
        mock_isfile.return_value = True
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = VMManager.create_vm("testvm", "fedora", "/path/to/fedora.iso")
        self.assertTrue(result.success)
        self.assertIn("created successfully", result.message)

    def test_create_vm_invalid_name(self):
        """Create VM rejects invalid VM name."""
        result = VMManager.create_vm("test vm!", "fedora", "/path/to/iso")
        self.assertFalse(result.success)
        self.assertIn("Invalid VM name", result.message)

    def test_create_vm_invalid_flavor(self):
        """Create VM rejects unknown flavor."""
        result = VMManager.create_vm("testvm", "nonexistent", "/path/to/iso")
        self.assertFalse(result.success)
        self.assertIn("Unknown flavour", result.message)

    @patch('services.virtualization.vm_manager.os.path.isfile')
    def test_create_vm_missing_iso(self, mock_isfile):
        """Create VM fails when ISO not found."""
        mock_isfile.return_value = False
        result = VMManager.create_vm("testvm", "fedora", "/missing/iso")
        self.assertFalse(result.success)
        self.assertIn("ISO file not found", result.message)

    @patch('services.virtualization.vm_manager.os.path.isfile')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_create_vm_virt_install_missing(self, mock_which, mock_isfile):
        """Create VM fails when virt-install not available."""
        mock_which.return_value = None
        mock_isfile.return_value = True
        result = VMManager.create_vm("testvm", "fedora", "/path/to/iso")
        self.assertFalse(result.success)
        self.assertIn("virt-install is not installed", result.message)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.os.path.isfile')
    @patch('services.virtualization.vm_manager.cached_which')
    @patch('services.virtualization.vm_manager.VMManager.get_default_storage_pool')
    def test_create_vm_swtpm_missing_for_windows11(self, mock_pool, mock_which, mock_isfile, mock_run):
        """Create VM fails for Windows 11 when swtpm missing."""
        mock_pool.return_value = "/var/lib/libvirt/images"
        mock_which.side_effect = lambda x: "/usr/bin/virt-install" if x == "virt-install" else None
        mock_isfile.return_value = True

        result = VMManager.create_vm("win11vm", "windows11", "/path/to/win11.iso")
        self.assertFalse(result.success)
        self.assertIn("swtpm", result.message)


class TestVMManagerVMOperations(unittest.TestCase):
    """Test VM start/stop/delete operations."""

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_start_vm_success(self, mock_which, mock_run):
        """Start VM succeeds."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = VMManager.start_vm("testvm")
        self.assertTrue(result.success)
        self.assertIn("started", result.message)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_start_vm_failure(self, mock_which, mock_run):
        """Start VM handles failure."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=1, stderr="VM not found")
        result = VMManager.start_vm("testvm")
        self.assertFalse(result.success)
        self.assertIn("Failed to start", result.message)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_stop_vm_success(self, mock_which, mock_run):
        """Stop VM sends shutdown signal."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=0)
        result = VMManager.stop_vm("testvm")
        self.assertTrue(result.success)
        self.assertIn("shutdown signal sent", result.message)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_force_stop_vm_success(self, mock_which, mock_run):
        """Force stop VM succeeds."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=0)
        result = VMManager.force_stop_vm("testvm")
        self.assertTrue(result.success)
        self.assertIn("force-stopped", result.message)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_delete_vm_success(self, mock_which, mock_run):
        """Delete VM succeeds."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=0)
        result = VMManager.delete_vm("testvm")
        self.assertTrue(result.success)
        self.assertIn("deleted", result.message)

    @patch('services.virtualization.vm_manager.subprocess.run')
    @patch('services.virtualization.vm_manager.cached_which')
    def test_delete_vm_with_storage(self, mock_which, mock_run):
        """Delete VM with storage removal flag."""
        mock_which.return_value = "/usr/bin/virsh"
        mock_run.return_value = MagicMock(returncode=0)
        result = VMManager.delete_vm("testvm", delete_storage=True)
        self.assertTrue(result.success)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("--remove-all-storage", args)


class TestVMManagerHelpers(unittest.TestCase):
    """Test helper methods."""

    @patch('services.virtualization.vm_manager.os.path.isdir')
    def test_get_default_storage_pool_system(self, mock_isdir):
        """Get default storage pool returns system path."""
        mock_isdir.return_value = True
        result = VMManager.get_default_storage_pool()
        self.assertEqual(result, "/var/lib/libvirt/images")

    @patch('services.virtualization.vm_manager.os.makedirs')
    @patch('services.virtualization.vm_manager.os.path.isdir')
    def test_get_default_storage_pool_user(self, mock_isdir, mock_makedirs):
        """Get default storage pool creates user path if system unavailable."""
        mock_isdir.return_value = False
        result = VMManager.get_default_storage_pool()
        self.assertIn(".local/share/loofi-vms", result)
        mock_makedirs.assert_called_once()

    @patch('services.virtualization.vm_manager.subprocess.run')
    def test_check_user_in_libvirt_group_true(self, mock_run):
        """Check user in libvirt group returns True."""
        mock_run.return_value = MagicMock(
            stdout="user libvirt wheel\n",
            returncode=0
        )
        result = VMManager.check_user_in_libvirt_group()
        self.assertTrue(result)

    @patch('services.virtualization.vm_manager.subprocess.run')
    def test_check_user_in_libvirt_group_false(self, mock_run):
        """Check user in libvirt group returns False."""
        mock_run.return_value = MagicMock(
            stdout="user wheel\n",
            returncode=0
        )
        result = VMManager.check_user_in_libvirt_group()
        self.assertFalse(result)

    @patch('services.virtualization.vm_manager.subprocess.run')
    def test_check_user_in_libvirt_group_failure(self, mock_run):
        """Check user in libvirt group returns False on failure."""
        mock_run.side_effect = OSError()
        result = VMManager.check_user_in_libvirt_group()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
