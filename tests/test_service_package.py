"""Tests for services/package/ modules.

Covers:
- services/package/base.py — BasePackageService (abstract)
- services/package/service.py — DnfPackageService, RpmOstreePackageService
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))

from core.executor.action_result import ActionResult
from services.package.base import BasePackageService
from services.package.service import (
    DnfPackageService,
    RpmOstreePackageService,
    get_package_service,
)


# ===========================================================================
# BasePackageService tests
# ===========================================================================

class TestBasePackageService(unittest.TestCase):
    """Test abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """BasePackageService cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BasePackageService()


# ===========================================================================
# DnfPackageService tests
# ===========================================================================

class TestDnfPackageServiceInstall(unittest.TestCase):
    """Test DnfPackageService install operation."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_install_success(self, mock_pm, mock_worker_class):
        """Install packages succeeds."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Installed successfully"
        )
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.install(["vim", "git"], description="Test install")

        self.assertTrue(result.success)
        mock_worker.start.assert_called_once()
        mock_worker.wait.assert_called_once()

    @patch('services.package.service.SystemManager.get_package_manager')
    def test_install_empty_packages(self, mock_pm):
        """Install fails with empty package list."""
        mock_pm.return_value = "dnf"
        service = DnfPackageService()
        result = service.install([])
        self.assertFalse(result.success)
        self.assertIn("No packages specified", result.message)

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_install_with_callback(self, mock_pm, mock_worker_class):
        """Install with progress callback wires signal."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="OK")
        mock_worker_class.return_value = mock_worker

        callback = MagicMock()
        service = DnfPackageService()
        result = service.install(["vim"], callback=callback)

        self.assertTrue(result.success)
        mock_worker.progress.connect.assert_called_once()


class TestDnfPackageServiceRemove(unittest.TestCase):
    """Test DnfPackageService remove operation."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_remove_success(self, mock_pm, mock_worker_class):
        """Remove packages succeeds."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Removed")
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.remove(["vim"])

        self.assertTrue(result.success)

    @patch('services.package.service.SystemManager.get_package_manager')
    def test_remove_empty_packages(self, mock_pm):
        """Remove fails with empty package list."""
        mock_pm.return_value = "dnf"
        service = DnfPackageService()
        result = service.remove([])
        self.assertFalse(result.success)


class TestDnfPackageServiceUpdate(unittest.TestCase):
    """Test DnfPackageService update operation."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_update_all_packages(self, mock_pm, mock_worker_class):
        """Update all packages succeeds."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Updated")
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.update()

        self.assertTrue(result.success)

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_update_specific_packages(self, mock_pm, mock_worker_class):
        """Update specific packages succeeds."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Updated")
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.update(packages=["vim", "git"])

        self.assertTrue(result.success)


class TestDnfPackageServiceSearch(unittest.TestCase):
    """Test DnfPackageService search operation."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_search_success(self, mock_pm, mock_worker_class):
        """Search returns matching packages."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Search complete",
            stdout="vim-enhanced.x86_64\nvim-common.noarch\n"
        )
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.search("vim")

        self.assertTrue(result.success)
        self.assertIn("matches", result.data)
        self.assertGreater(len(result.data["matches"]), 0)

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_search_with_limit(self, mock_pm, mock_worker_class):
        """Search respects limit parameter."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        stdout = "\n".join([f"package{i}.x86_64" for i in range(100)])
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Search complete",
            stdout=stdout
        )
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.search("package", limit=10)

        self.assertTrue(result.success)
        self.assertLessEqual(len(result.data["matches"]), 10)


class TestDnfPackageServiceInfo(unittest.TestCase):
    """Test DnfPackageService info operation."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_info_success(self, mock_pm, mock_worker_class):
        """Info returns package information."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Info retrieved",
            stdout="Name: vim\nVersion: 8.2\n"
        )
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.info("vim")

        self.assertTrue(result.success)
        self.assertIn("package", result.data)
        self.assertEqual(result.data["package"], "vim")


class TestDnfPackageServiceList(unittest.TestCase):
    """Test DnfPackageService list operations."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.SystemManager.get_package_manager')
    def test_list_installed_success(self, mock_pm, mock_worker_class):
        """List installed returns package list."""
        mock_pm.return_value = "dnf"
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Listed packages",
            stdout="vim.x86_64\ngit.x86_64\nbash.x86_64\n"
        )
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.list_installed()

        self.assertTrue(result.success)
        self.assertIn("packages", result.data)
        self.assertGreater(result.data["count"], 0)

    @patch('services.package.service.CommandWorker')
    def test_is_installed_true(self, mock_worker_class):
        """is_installed returns True for installed package."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Found", exit_code=0)
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.is_installed("vim")

        self.assertTrue(result)

    @patch('services.package.service.CommandWorker')
    def test_is_installed_false(self, mock_worker_class):
        """is_installed returns False for non-installed package."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=False, message="Not found", exit_code=1)
        mock_worker_class.return_value = mock_worker

        service = DnfPackageService()
        result = service.is_installed("nonexistent")

        self.assertFalse(result)


# ===========================================================================
# RpmOstreePackageService tests
# ===========================================================================

class TestRpmOstreePackageServiceInstall(unittest.TestCase):
    """Test RpmOstreePackageService install operation."""

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.logger')
    def test_install_with_apply_live_success(self, mock_logger, mock_worker_class):
        """Install with --apply-live succeeds."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            exit_code=0,
            message="Installed"
        )
        mock_worker_class.return_value = mock_worker

        service = RpmOstreePackageService()
        result = service.install(["vim"])

        self.assertTrue(result.success)

    @patch('services.package.service.CommandWorker')
    @patch('services.package.service.logger')
    def test_install_fallback_without_apply_live(self, mock_logger, mock_worker_class):
        """Install falls back to regular install when --apply-live fails."""
        mock_worker_fail = MagicMock()
        mock_worker_fail.get_result.return_value = ActionResult(
            success=False,
            message="Failed",
            exit_code=1,
            stdout="cannot apply live"
        )
        mock_worker_success = MagicMock()
        mock_worker_success.get_result.return_value = ActionResult(
            success=True,
            exit_code=0,
            message="Installed (reboot required)"
        )
        mock_worker_class.side_effect = [mock_worker_fail, mock_worker_success]

        service = RpmOstreePackageService()
        result = service.install(["vim"])

        self.assertTrue(result.success)
        self.assertTrue(result.needs_reboot)

    def test_install_empty_packages(self):
        """Install fails with empty package list."""
        service = RpmOstreePackageService()
        result = service.install([])
        self.assertFalse(result.success)


class TestRpmOstreePackageServiceRemove(unittest.TestCase):
    """Test RpmOstreePackageService remove operation."""

    @patch('services.package.service.CommandWorker')
    def test_remove_success(self, mock_worker_class):
        """Remove packages marks reboot needed."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Removed")
        mock_worker_class.return_value = mock_worker

        service = RpmOstreePackageService()
        result = service.remove(["vim"])

        self.assertTrue(result.success)
        self.assertTrue(result.needs_reboot)


class TestRpmOstreePackageServiceUpdate(unittest.TestCase):
    """Test RpmOstreePackageService update operation."""

    @patch('services.package.service.CommandWorker')
    def test_update_all_packages(self, mock_worker_class):
        """Update system marks reboot needed."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Upgraded")
        mock_worker_class.return_value = mock_worker

        service = RpmOstreePackageService()
        result = service.update()

        self.assertTrue(result.success)
        self.assertTrue(result.needs_reboot)

    def test_update_specific_packages_not_supported(self):
        """Update specific packages returns error."""
        service = RpmOstreePackageService()
        result = service.update(packages=["vim"])
        self.assertFalse(result.success)
        self.assertIn("does not support selective", result.message)


class TestRpmOstreePackageServiceQueryOps(unittest.TestCase):
    """Test RpmOstreePackageService query operations."""

    def test_search_not_implemented(self):
        """Search returns not implemented."""
        service = RpmOstreePackageService()
        result = service.search("vim")
        self.assertFalse(result.success)
        self.assertIn("not implemented", result.message)

    @patch('services.package.service.CommandWorker')
    def test_info_uses_rpm(self, mock_worker_class):
        """Info delegates to rpm -qi."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Info retrieved",
            stdout="Name: vim\nVersion: 8.2\n"
        )
        mock_worker_class.return_value = mock_worker

        service = RpmOstreePackageService()
        result = service.info("vim")

        self.assertTrue(result.success)
        self.assertIn("package", result.data)

    @patch('services.package.service.CommandWorker')
    def test_list_installed_uses_rpm(self, mock_worker_class):
        """List installed delegates to rpm -qa."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(
            success=True,
            message="Listed packages",
            stdout="vim-8.2\ngit-2.39\n"
        )
        mock_worker_class.return_value = mock_worker

        service = RpmOstreePackageService()
        result = service.list_installed()

        self.assertTrue(result.success)
        self.assertGreater(result.data["count"], 0)

    @patch('services.package.service.CommandWorker')
    def test_is_installed_true(self, mock_worker_class):
        """is_installed returns True for installed package."""
        mock_worker = MagicMock()
        mock_worker.get_result.return_value = ActionResult(success=True, message="Package found", exit_code=0)
        mock_worker_class.return_value = mock_worker

        service = RpmOstreePackageService()
        result = service.is_installed("vim")

        self.assertTrue(result)


# ===========================================================================
# Factory function tests
# ===========================================================================

class TestGetPackageService(unittest.TestCase):
    """Test package service factory function."""

    @patch('services.package.service.SystemManager.get_package_manager')
    def test_returns_dnf_service_for_traditional_fedora(self, mock_pm):
        """Factory returns DnfPackageService for traditional Fedora."""
        mock_pm.return_value = "dnf"
        service = get_package_service()
        self.assertIsInstance(service, DnfPackageService)

    @patch('services.package.service.SystemManager.get_package_manager')
    def test_returns_rpm_ostree_service_for_atomic_fedora(self, mock_pm):
        """Factory returns RpmOstreePackageService for Atomic Fedora."""
        mock_pm.return_value = "rpm-ostree"
        service = get_package_service()
        self.assertIsInstance(service, RpmOstreePackageService)


if __name__ == '__main__':
    unittest.main()
