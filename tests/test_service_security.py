"""Tests for services/security/ modules.

Covers:
- services/security/firewall.py — FirewallManager
- services/security/secureboot.py — SecureBootManager
"""
# pylint: disable=protected-access

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from services.security.firewall import (
    FirewallManager,
)
from services.security.secureboot import (
    SecureBootManager,
)

# Add source path
sys.path.insert(0, os.path.join(os.path.dirname(
    __file__), '..', 'loofi-fedora-tweaks'))


# ===========================================================================
# FirewallManager tests
# ===========================================================================


class TestFirewallManagerAvailability(unittest.TestCase):
    """Test FirewallManager availability checking."""

    def setUp(self):
        """Reset cached availability before each test."""
        FirewallManager._available_cached = None

    @patch('services.security.firewall.subprocess.run')
    def test_is_available_success(self, mock_run):
        """FirewallManager detects firewall-cmd is available."""
        mock_run.return_value = MagicMock(returncode=0)
        result = FirewallManager.is_available()
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["firewall-cmd", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

    @patch('services.security.firewall.subprocess.run')
    def test_is_available_not_found(self, mock_run):
        """FirewallManager handles firewall-cmd not installed."""
        mock_run.side_effect = OSError("Command not found")
        result = FirewallManager.is_available()
        self.assertFalse(result)

    @patch('services.security.firewall.subprocess.run')
    def test_is_available_cached(self, mock_run):
        """Availability check is cached after first call."""
        mock_run.return_value = MagicMock(returncode=0)
        first_result = FirewallManager.is_available()
        second_result = FirewallManager.is_available()
        self.assertTrue(first_result)
        self.assertTrue(second_result)
        mock_run.assert_called_once()  # Only called once

    @patch('services.security.firewall.subprocess.run')
    def test_is_running_success(self, mock_run):
        """FirewallManager detects firewalld is running."""
        mock_run.return_value = MagicMock(stdout="running\n", returncode=0)
        result = FirewallManager.is_running()
        self.assertTrue(result)

    @patch('services.security.firewall.subprocess.run')
    def test_is_running_not_running(self, mock_run):
        """FirewallManager detects firewalld is stopped."""
        mock_run.return_value = MagicMock(stdout="not running\n", returncode=1)
        result = FirewallManager.is_running()
        self.assertFalse(result)


class TestFirewallManagerInfo(unittest.TestCase):
    """Test FirewallManager information queries."""

    @patch('services.security.firewall.subprocess.run')
    def test_get_default_zone_success(self, mock_run):
        """Get default zone returns zone name."""
        mock_run.return_value = MagicMock(stdout="public\n", returncode=0)
        result = FirewallManager.get_default_zone()
        self.assertEqual(result, "public")

    @patch('services.security.firewall.subprocess.run')
    def test_get_default_zone_failure(self, mock_run):
        """Get default zone returns empty on error."""
        mock_run.return_value = MagicMock(returncode=1)
        result = FirewallManager.get_default_zone()
        self.assertEqual(result, "")

    @patch('services.security.firewall.subprocess.run')
    def test_get_zones_success(self, mock_run):
        """List all zones returns list of zone names."""
        mock_run.return_value = MagicMock(
            stdout="block dmz drop home public\n", returncode=0)
        result = FirewallManager.get_zones()
        self.assertEqual(result, ["block", "dmz", "drop", "home", "public"])

    @patch('services.security.firewall.subprocess.run')
    def test_get_active_zones_success(self, mock_run):
        """Get active zones parses interfaces correctly."""
        mock_run.return_value = MagicMock(
            stdout=(
                "public\n  interfaces: eth0 wlan0\n"
                "work\n  interfaces: vpn0\n"
            ),
            returncode=0
        )
        result = FirewallManager.get_active_zones()
        self.assertEqual(
            result, {"public": ["eth0", "wlan0"], "work": ["vpn0"]})

    @patch('services.security.firewall.subprocess.run')
    def test_list_ports_success(self, mock_run):
        """List ports returns port/protocol list."""
        mock_run.return_value = MagicMock(
            stdout="80/tcp 443/tcp 8080/tcp\n", returncode=0)
        result = FirewallManager.list_ports()
        self.assertEqual(result, ["80/tcp", "443/tcp", "8080/tcp"])

    @patch('services.security.firewall.subprocess.run')
    def test_list_ports_empty(self, mock_run):
        """List ports returns empty list when no ports open."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = FirewallManager.list_ports()
        self.assertEqual(result, [])


class TestFirewallManagerCommandBuilders(unittest.TestCase):
    """Test PrivilegedCommand integration (v2.11.0 TASK-005)."""

    def test_firewall_cmd_builder_returns_tuple(self):
        """firewall_cmd() returns CommandTuple with correct structure."""
        from utils.commands import PrivilegedCommand
        result = PrivilegedCommand.firewall_cmd("--list-all")

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        binary, args, desc = result
        self.assertEqual(binary, "pkexec")
        self.assertIn("firewall-cmd", args)
        self.assertIn("--list-all", args)
        self.assertIsInstance(desc, str)

    def test_firewall_reload_builder_returns_tuple(self):
        """firewall_reload() returns CommandTuple with correct structure."""
        from utils.commands import PrivilegedCommand
        result = PrivilegedCommand.firewall_reload()

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        binary, args, desc = result
        self.assertEqual(binary, "pkexec")
        self.assertIn("firewall-cmd", args)
        self.assertIn("--reload", args)
        self.assertIn("reload", desc.lower())

    def test_firewall_cmd_never_uses_shell_true(self):
        """firewall_cmd returns argument list, not shell string."""
        from utils.commands import PrivilegedCommand
        _, args, _ = PrivilegedCommand.firewall_cmd("--add-port=80/tcp")

        self.assertIsInstance(args, list)
        self.assertGreater(len(args), 0)
        self.assertEqual(args[0], "firewall-cmd")


class TestFirewallManagerOperations(unittest.TestCase):
    """Test FirewallManager port/service operations."""

    @patch('services.security.firewall.FirewallManager._reload')
    @patch('services.security.firewall.subprocess.run')
    def test_open_port_success(self, mock_run, mock_reload):
        """Open port succeeds and reloads firewall."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        mock_reload.return_value = True
        result = FirewallManager.open_port("8080", "tcp", permanent=True)
        self.assertTrue(result.success)
        self.assertIn("8080/tcp", result.message)
        mock_reload.assert_called_once()

    @patch('services.security.firewall.subprocess.run')
    def test_open_port_failure(self, mock_run):
        """Open port handles failure."""
        mock_run.return_value = MagicMock(
            returncode=1, stderr="Error: port in use")
        result = FirewallManager.open_port("8080", "tcp")
        self.assertFalse(result.success)
        self.assertIn("Failed", result.message)

    @patch('services.security.firewall.FirewallManager._reload')
    @patch('services.security.firewall.subprocess.run')
    def test_add_service_success(self, mock_run, mock_reload):
        """Add service succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        mock_reload.return_value = True
        result = FirewallManager.add_service("http", permanent=True)
        self.assertTrue(result.success)
        self.assertIn("http", result.message)

    @patch('services.security.firewall.subprocess.run')
    def test_list_services_success(self, mock_run):
        """List services returns sorted service names."""
        mock_run.return_value = MagicMock(
            stdout="ssh http https\n", returncode=0)
        result = FirewallManager.list_services()
        self.assertEqual(result, ["http", "https", "ssh"])


class TestFirewallManagerStatus(unittest.TestCase):
    """Test comprehensive status gathering."""

    @patch('services.security.firewall.daemon_client.call_json')
    def test_get_status_running(self, mock_call_json):
        """Get status from daemon payload when available."""
        mock_call_json.return_value = {
            "running": True,
            "default_zone": "public",
            "active_zones": {"public": ["eth0"]},
            "ports": ["80/tcp"],
            "services": ["ssh"],
            "rich_rules": [],
        }

        status = FirewallManager.get_status()

        self.assertTrue(status.running)
        self.assertEqual(status.default_zone, "public")
        self.assertEqual(status.active_zones, {"public": ["eth0"]})
        self.assertEqual(status.ports, ["80/tcp"])
        self.assertEqual(status.services, ["ssh"])
        mock_call_json.assert_called_once_with("FirewallGetStatus")

    @patch('services.security.firewall.daemon_client.call_json')
    def test_get_status_not_running(self, mock_call_json):
        """Get minimal info when daemon reports firewall stopped."""
        mock_call_json.return_value = {"running": False}
        status = FirewallManager.get_status()
        self.assertFalse(status.running)
        self.assertEqual(status.default_zone, "")
        mock_call_json.assert_called_once_with("FirewallGetStatus")


# ===========================================================================
# SecureBootManager tests
# ===========================================================================

class TestSecureBootManagerStatus(unittest.TestCase):
    """Test SecureBootManager status checking."""

    @patch('services.security.secureboot.subprocess.run')
    def test_get_status_enabled(self, mock_run):
        """Get status detects Secure Boot enabled."""
        mock_run.side_effect = [
            MagicMock(stdout="SecureBoot enabled\n", returncode=0),
            MagicMock(stdout="[key data]\n", returncode=0),
            MagicMock(stdout="", returncode=0),
        ]
        status = SecureBootManager.get_status()
        self.assertTrue(status.secure_boot_enabled)
        self.assertTrue(status.mok_enrolled)
        self.assertFalse(status.pending_mok)
        self.assertIn("SecureBoot enabled", status.status_message)

    @patch('services.security.secureboot.subprocess.run')
    def test_get_status_mokutil_not_found(self, mock_run):
        """Get status handles mokutil not installed."""
        mock_run.side_effect = FileNotFoundError()
        status = SecureBootManager.get_status()
        self.assertFalse(status.secure_boot_enabled)
        self.assertIn("mokutil not installed", status.status_message)


class TestSecureBootManagerKeyGeneration(unittest.TestCase):
    """Test MOK key generation."""

    @patch('services.security.secureboot.os.chmod')
    @patch('services.security.secureboot.subprocess.run')
    @patch('services.security.secureboot.Path.mkdir')
    def test_generate_key_success(self, mock_mkdir, mock_run, mock_chmod):
        """Generate key creates key pair successfully."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = SecureBootManager.generate_key("password123")
        self.assertTrue(result.success)
        self.assertIn("Keys generated", result.message)
        mock_mkdir.assert_called_once()
        mock_chmod.assert_called_once()

    def test_generate_key_weak_password(self):
        """Generate key rejects short password."""
        result = SecureBootManager.generate_key("weak")
        self.assertFalse(result.success)
        self.assertIn("at least 8 characters", result.message)

    @patch('services.security.secureboot.subprocess.run')
    @patch('services.security.secureboot.Path.mkdir')
    def test_generate_key_openssl_failure(self, _mock_mkdir, mock_run):
        """Generate key handles openssl failure."""
        mock_run.return_value = MagicMock(returncode=1, stderr="OpenSSL error")
        result = SecureBootManager.generate_key("password123")
        self.assertFalse(result.success)
        self.assertIn("Key generation failed", result.message)


class TestSecureBootManagerKeyImport(unittest.TestCase):
    """Test MOK key import."""

    @patch('services.security.secureboot.subprocess.run')
    @patch('services.security.secureboot.Path.exists')
    def test_import_key_success(self, mock_exists, mock_run):
        """Import key queues MOK for enrollment."""
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        result = SecureBootManager.import_key("password123")
        self.assertTrue(result.success)
        self.assertTrue(result.requires_reboot)
        self.assertIn("queued for enrollment", result.message)

    @patch('services.security.secureboot.Path.exists')
    def test_import_key_no_key(self, mock_exists):
        """Import key fails when key doesn't exist."""
        mock_exists.return_value = False
        result = SecureBootManager.import_key("password123")
        self.assertFalse(result.success)
        self.assertIn("No MOK key found", result.message)


class TestSecureBootManagerModuleSigning(unittest.TestCase):
    """Test kernel module signing."""

    @patch('services.security.secureboot.subprocess.run')
    @patch('services.security.secureboot.os.path.exists')
    @patch('services.security.secureboot.Path.exists')
    @patch('glob.glob')
    def test_sign_module_success(
        self,
        mock_glob,
        mock_path_exists,
        mock_os_exists,
        mock_run,
    ):
        """Sign module succeeds with valid keys and module."""
        mock_path_exists.return_value = True
        mock_os_exists.return_value = True
        mock_glob.return_value = ["/usr/src/kernels/5.15.0/scripts/sign-file"]
        mock_run.return_value = MagicMock(returncode=0)

        result = SecureBootManager.sign_module("/lib/modules/test.ko")
        self.assertTrue(result.success)
        self.assertIn("signed successfully", result.message)

    @patch('services.security.secureboot.Path.exists')
    def test_sign_module_no_keys(self, mock_exists):
        """Sign module fails when keys don't exist."""
        mock_exists.return_value = False
        result = SecureBootManager.sign_module("/lib/modules/test.ko")
        self.assertFalse(result.success)
        self.assertIn("MOK keys not found", result.message)

    @patch('services.security.secureboot.os.path.exists')
    @patch('services.security.secureboot.Path.exists')
    def test_sign_module_not_found(self, mock_path_exists, mock_os_exists):
        """Sign module fails when module file doesn't exist."""
        mock_path_exists.return_value = True
        mock_os_exists.return_value = False
        result = SecureBootManager.sign_module("/lib/modules/missing.ko")
        self.assertFalse(result.success)
        self.assertIn("Module not found", result.message)

    @patch('services.security.secureboot.Path.exists')
    @patch('services.security.secureboot.os.path.exists')
    @patch('glob.glob')
    def test_sign_module_no_sign_file_utility(
        self,
        mock_glob,
        mock_os_exists,
        mock_path_exists,
    ):
        """Sign module fails when sign-file utility not found."""
        mock_path_exists.return_value = True
        mock_os_exists.return_value = True
        mock_glob.return_value = []
        result = SecureBootManager.sign_module("/lib/modules/test.ko")
        self.assertFalse(result.success)
        self.assertIn("sign-file utility not found", result.message)


class TestSecureBootManagerHelpers(unittest.TestCase):
    """Test helper methods."""

    @patch('services.security.secureboot.Path.exists')
    def test_has_keys_true(self, mock_exists):
        """has_keys returns True when both keys exist."""
        mock_exists.return_value = True
        result = SecureBootManager.has_keys()
        self.assertTrue(result)

    @patch('services.security.secureboot.Path.exists')
    def test_has_keys_false(self, mock_exists):
        """has_keys returns False when keys missing."""
        mock_exists.return_value = False
        result = SecureBootManager.has_keys()
        self.assertFalse(result)

    @patch('services.security.secureboot.Path.exists')
    def test_get_key_path_exists(self, mock_exists):
        """get_key_path returns path when key exists."""
        mock_exists.return_value = True
        result = SecureBootManager.get_key_path()
        self.assertIsInstance(result, Path)

    @patch('services.security.secureboot.Path.exists')
    def test_get_key_path_not_exists(self, mock_exists):
        """get_key_path returns None when key missing."""
        mock_exists.return_value = False
        result = SecureBootManager.get_key_path()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
