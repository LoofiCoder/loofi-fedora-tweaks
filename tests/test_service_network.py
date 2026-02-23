"""Tests for services/network/ modules.

Covers:
- services/network/network.py — NetworkUtils
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))

from services.network.network import NetworkUtils


# ===========================================================================
# NetworkUtils tests
# ===========================================================================

class TestNetworkUtilsScanWifi(unittest.TestCase):
    """Test WiFi scanning."""

    @patch('services.network.network.subprocess.run')
    def test_scan_wifi_success(self, mock_run):
        """Scan WiFi returns parsed network list."""
        mock_run.return_value = MagicMock(
            stdout="MyNetwork:85:WPA2:no\nCoffeeShop:70:Open:no\nHome:95::yes\n",
            returncode=0
        )
        result = NetworkUtils.scan_wifi()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("MyNetwork", "85%", "WPA2", ""))
        self.assertEqual(result[1], ("CoffeeShop", "70%", "Open", ""))
        self.assertEqual(result[2], ("Home", "95%", "Open", "Connected"))

    @patch('services.network.network.subprocess.run')
    def test_scan_wifi_hidden_ssid(self, mock_run):
        """Scan WiFi handles hidden SSID."""
        mock_run.return_value = MagicMock(stdout=":75:WPA2:no\n", returncode=0)
        result = NetworkUtils.scan_wifi()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "(Hidden)")

    @patch('services.network.network.subprocess.run')
    def test_scan_wifi_empty(self, mock_run):
        """Scan WiFi returns empty list when no networks."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = NetworkUtils.scan_wifi()
        self.assertEqual(result, [])

    @patch('services.network.network.subprocess.run')
    def test_scan_wifi_failure(self, mock_run):
        """Scan WiFi handles command failure."""
        mock_run.side_effect = OSError("nmcli not found")
        result = NetworkUtils.scan_wifi()
        self.assertEqual(result, [])

    @patch('services.network.network.subprocess.run')
    def test_scan_wifi_timeout(self, mock_run):
        """Scan WiFi handles timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 15)
        result = NetworkUtils.scan_wifi()
        self.assertEqual(result, [])


class TestNetworkUtilsVPN(unittest.TestCase):
    """Test VPN connection listing."""

    @patch('services.network.network.subprocess.run')
    def test_load_vpn_connections_success(self, mock_run):
        """Load VPN connections returns VPN list."""
        mock_run.return_value = MagicMock(
            stdout="Work VPN:vpn:yes\nHome VPN:wireguard:no\nEthernet:ethernet:yes\n",
            returncode=0
        )
        result = NetworkUtils.load_vpn_connections()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ("Work VPN", "vpn", "🟢 Active"))
        self.assertEqual(result[1], ("Home VPN", "wireguard", "Inactive"))

    @patch('services.network.network.subprocess.run')
    def test_load_vpn_connections_openvpn(self, mock_run):
        """Load VPN connections detects OpenVPN."""
        mock_run.return_value = MagicMock(stdout="Server:openvpn:yes\n", returncode=0)
        result = NetworkUtils.load_vpn_connections()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("Server", "openvpn", "🟢 Active"))

    @patch('services.network.network.subprocess.run')
    def test_load_vpn_connections_empty(self, mock_run):
        """Load VPN connections returns empty when no VPNs."""
        mock_run.return_value = MagicMock(stdout="Ethernet:ethernet:yes\n", returncode=0)
        result = NetworkUtils.load_vpn_connections()
        self.assertEqual(result, [])

    @patch('services.network.network.subprocess.run')
    def test_load_vpn_connections_failure(self, mock_run):
        """Load VPN connections handles failure."""
        mock_run.side_effect = OSError()
        result = NetworkUtils.load_vpn_connections()
        self.assertEqual(result, [])


class TestNetworkUtilsDNS(unittest.TestCase):
    """Test DNS detection."""

    @patch('services.network.network.subprocess.run')
    def test_detect_current_dns_success(self, mock_run):
        """Detect DNS returns comma-separated servers."""
        mock_run.return_value = MagicMock(
            stdout="IP4.DNS[1]:8.8.8.8\nIP4.DNS[2]:8.8.4.4\nIP4.DNS[1]:1.1.1.1\n",
            returncode=0
        )
        result = NetworkUtils.detect_current_dns()
        self.assertIn("8.8.8.8", result)
        self.assertIn("8.8.4.4", result)
        self.assertIn("1.1.1.1", result)

    @patch('services.network.network.subprocess.run')
    def test_detect_current_dns_empty(self, mock_run):
        """Detect DNS returns empty when no DNS configured."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = NetworkUtils.detect_current_dns()
        self.assertEqual(result, "")

    @patch('services.network.network.subprocess.run')
    def test_detect_current_dns_failure(self, mock_run):
        """Detect DNS handles failure."""
        mock_run.side_effect = OSError()
        result = NetworkUtils.detect_current_dns()
        self.assertEqual(result, "")


class TestNetworkUtilsConnection(unittest.TestCase):
    """Test active connection detection."""

    @patch('services.network.network.subprocess.run')
    def test_get_active_connection_wifi(self, mock_run):
        """Get active connection returns WiFi name."""
        mock_run.return_value = MagicMock(stdout="MyNetwork:wifi\n", returncode=0)
        result = NetworkUtils.get_active_connection()
        self.assertEqual(result, "MyNetwork")

    @patch('services.network.network.subprocess.run')
    def test_get_active_connection_ethernet(self, mock_run):
        """Get active connection returns Ethernet name."""
        mock_run.return_value = MagicMock(stdout="Wired connection 1:ethernet\n", returncode=0)
        result = NetworkUtils.get_active_connection()
        self.assertEqual(result, "Wired connection 1")

    @patch('services.network.network.subprocess.run')
    def test_get_active_connection_none(self, mock_run):
        """Get active connection returns None when no active connection."""
        mock_run.return_value = MagicMock(stdout="VPN:vpn\n", returncode=0)
        result = NetworkUtils.get_active_connection()
        self.assertIsNone(result)

    @patch('services.network.network.subprocess.run')
    def test_get_active_connection_failure(self, mock_run):
        """Get active connection returns None on failure."""
        mock_run.side_effect = OSError()
        result = NetworkUtils.get_active_connection()
        self.assertIsNone(result)


class TestNetworkUtilsPrivacy(unittest.TestCase):
    """Test hostname privacy checking."""

    @patch('services.network.network.subprocess.run')
    def test_check_hostname_privacy_hidden(self, mock_run):
        """Check hostname privacy detects hidden hostname."""
        mock_run.return_value = MagicMock(stdout="ipv4.dhcp-send-hostname:no\n", returncode=0)
        result = NetworkUtils.check_hostname_privacy("MyConnection")
        self.assertTrue(result)

    @patch('services.network.network.subprocess.run')
    def test_check_hostname_privacy_visible(self, mock_run):
        """Check hostname privacy detects visible hostname."""
        mock_run.return_value = MagicMock(stdout="ipv4.dhcp-send-hostname:yes\n", returncode=0)
        result = NetworkUtils.check_hostname_privacy("MyConnection")
        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_check_hostname_privacy_default_visible(self, mock_run):
        """Check hostname privacy defaults to visible (False) on parse error."""
        mock_run.return_value = MagicMock(stdout="invalid:data\n", returncode=0)
        result = NetworkUtils.check_hostname_privacy("MyConnection")
        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_check_hostname_privacy_failure(self, mock_run):
        """Check hostname privacy returns None on failure."""
        mock_run.side_effect = OSError()
        result = NetworkUtils.check_hostname_privacy("MyConnection")
        self.assertIsNone(result)


class TestNetworkUtilsReactivate(unittest.TestCase):
    """Test connection reactivation."""

    @patch('services.network.network.subprocess.run')
    def test_reactivate_connection_success(self, mock_run):
        """Reactivate connection succeeds."""
        mock_run.return_value = MagicMock(returncode=0)
        result = NetworkUtils.reactivate_connection("MyConnection")
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["nmcli", "con", "up", "MyConnection"],
            capture_output=True,
            timeout=10
        )

    @patch('services.network.network.subprocess.run')
    def test_reactivate_connection_failure(self, mock_run):
        """Reactivate connection handles failure."""
        mock_run.side_effect = OSError()
        result = NetworkUtils.reactivate_connection("MyConnection")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
