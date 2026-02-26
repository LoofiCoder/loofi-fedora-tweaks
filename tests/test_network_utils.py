"""
Tests for utils/network_utils.py (v34.0).
Covers scan_wifi, load_vpn_connections, detect_current_dns,
get_active_connection, check_hostname_privacy, reactivate_connection.
"""
import os
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

from services.network.network import NetworkUtils

sys.path.append(os.path.join(os.path.dirname(
    __file__), '..', 'loofi-fedora-tweaks'))


class TestScanWifi(unittest.TestCase):
    """Tests for NetworkUtils.scan_wifi()."""

    @patch('services.network.network.subprocess.run')
    def test_scan_returns_networks(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="MyNetwork:85:WPA2:yes\nGuest:40:Open:no\n"
        )
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ("MyNetwork", "85%", "WPA2", "Connected"))
        self.assertEqual(rows[1], ("Guest", "40%", "Open", ""))

    @patch('services.network.network.subprocess.run')
    def test_scan_hidden_ssid(self, mock_run):
        mock_run.return_value = MagicMock(stdout=":60:WPA2:no\n")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "(Hidden)")

    @patch('services.network.network.subprocess.run')
    def test_scan_open_security(self, mock_run):
        mock_run.return_value = MagicMock(stdout="CafeWifi:72::no\n")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "Open")

    @patch('services.network.network.subprocess.run')
    def test_scan_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_scan_blank_lines_skipped(self, mock_run):
        mock_run.return_value = MagicMock(stdout="\n\nAP:50:WPA:no\n\n")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(len(rows), 1)

    @patch('services.network.network.subprocess.run')
    def test_scan_malformed_line_skipped(self, mock_run):
        mock_run.return_value = MagicMock(stdout="only_two:fields\n")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_scan_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 15)
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_scan_oserror(self, mock_run):
        mock_run.side_effect = OSError("nmcli not found")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_scan_subprocess_error(self, mock_run):
        mock_run.side_effect = subprocess.SubprocessError("fail")
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows, [])


class TestLoadVpnConnections(unittest.TestCase):
    """Tests for NetworkUtils.load_vpn_connections()."""

    @patch('services.network.network.subprocess.run')
    def test_vpn_connections_found(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout=(
                "MyEthernet:802-3-ethernet:yes\n"
                "WorkVPN:vpn:yes\n"
                "HomeWG:wireguard:no\n"
            )
        )
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ("WorkVPN", "vpn", "🟢 Active"))
        self.assertEqual(rows[1], ("HomeWG", "wireguard", "Inactive"))

    @patch('services.network.network.subprocess.run')
    def test_openvpn_detected(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="CorpVPN:openvpn:no\n"
        )
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "CorpVPN")

    @patch('services.network.network.subprocess.run')
    def test_no_vpn_connections(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="WiFi:802-11-wireless:yes\n"
        )
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_vpn_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="")
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_vpn_malformed_line_skipped(self, mock_run):
        mock_run.return_value = MagicMock(stdout="vpn_only_two:fields\n")
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_vpn_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 5)
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(rows, [])

    @patch('services.network.network.subprocess.run')
    def test_vpn_oserror(self, mock_run):
        mock_run.side_effect = OSError("nmcli not found")
        rows = NetworkUtils.load_vpn_connections()
        self.assertEqual(rows, [])


class TestDetectCurrentDns(unittest.TestCase):
    """Tests for NetworkUtils.detect_current_dns()."""

    @patch('services.network.network.subprocess.run')
    def test_multiple_dns_servers(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="IP4.DNS[1]:8.8.8.8\nIP4.DNS[2]:1.1.1.1\n"
        )
        dns = NetworkUtils.detect_current_dns()
        self.assertIn("8.8.8.8", dns)
        self.assertIn("1.1.1.1", dns)

    @patch('services.network.network.subprocess.run')
    def test_single_dns_server(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="IP4.DNS[1]:9.9.9.9\n"
        )
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "9.9.9.9")

    @patch('services.network.network.subprocess.run')
    def test_no_dns_found(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="IP4.ADDRESS[1]:192.168.1.2/24\n")
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "192.168.1.2/24")

    @patch('services.network.network.subprocess.run')
    def test_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="")
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "")

    @patch('services.network.network.subprocess.run')
    def test_empty_value_after_colon(self, mock_run):
        mock_run.return_value = MagicMock(stdout="IP4.DNS[1]:\n")
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "")

    @patch('services.network.network.subprocess.run')
    def test_deduplication(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="IP4.DNS[1]:8.8.8.8\nIP4.DNS[1]:8.8.8.8\n"
        )
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "8.8.8.8")

    @patch('services.network.network.subprocess.run')
    def test_dns_sorted(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="IP4.DNS[1]:9.9.9.9\nIP4.DNS[2]:1.1.1.1\n"
        )
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "1.1.1.1, 9.9.9.9")

    @patch('services.network.network.subprocess.run')
    def test_dns_oserror(self, mock_run):
        mock_run.side_effect = OSError("nmcli not found")
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "")

    @patch('services.network.network.subprocess.run')
    def test_dns_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 5)
        dns = NetworkUtils.detect_current_dns()
        self.assertEqual(dns, "")


class TestGetActiveConnection(unittest.TestCase):
    """Tests for NetworkUtils.get_active_connection()."""

    @patch('services.network.network.subprocess.run')
    def test_wifi_connection_active(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="HomeNetwork:wifi\nlo:loopback\n"
        )
        conn = NetworkUtils.get_active_connection()
        self.assertEqual(conn, "HomeNetwork")

    @patch('services.network.network.subprocess.run')
    def test_ethernet_connection_active(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="Wired:ethernet\nlo:loopback\n"
        )
        conn = NetworkUtils.get_active_connection()
        self.assertEqual(conn, "Wired")

    @patch('services.network.network.subprocess.run')
    def test_no_active_connection(self, mock_run):
        mock_run.return_value = MagicMock(stdout="lo:loopback\n")
        conn = NetworkUtils.get_active_connection()
        self.assertIsNone(conn)

    @patch('services.network.network.subprocess.run')
    def test_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="")
        conn = NetworkUtils.get_active_connection()
        self.assertIsNone(conn)

    @patch('services.network.network.subprocess.run')
    def test_oserror(self, mock_run):
        mock_run.side_effect = OSError("nmcli missing")
        conn = NetworkUtils.get_active_connection()
        self.assertIsNone(conn)

    @patch('services.network.network.subprocess.run')
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 5)
        conn = NetworkUtils.get_active_connection()
        self.assertIsNone(conn)

    @patch('services.network.network.subprocess.run')
    def test_malformed_rows_return_none(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="bad_row_without_delimiter\nOffice\\:WiFi:wifi\n"
        )

        conn = NetworkUtils.get_active_connection()

        self.assertIsNone(conn)

    @patch('services.network.network.subprocess.run')
    def test_non_target_types_not_misclassified_by_name(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="wifi-tools:bridge\nethernet-lab:vpn\n"
        )

        conn = NetworkUtils.get_active_connection()

        self.assertIsNone(conn)

    @patch('services.network.network.subprocess.run')
    def test_selects_first_valid_wifi_or_ethernet_row(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="lo:loopback\nCorpVPN:vpn\nHome:wifi\nWired:ethernet\n"
        )

        conn = NetworkUtils.get_active_connection()

        self.assertEqual(conn, "Home")


class TestCheckHostnamePrivacy(unittest.TestCase):
    """Tests for NetworkUtils.check_hostname_privacy()."""

    @patch('services.network.network.subprocess.run')
    def test_hostname_hidden(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="ipv4.dhcp-send-hostname:no\n"
        )
        result = NetworkUtils.check_hostname_privacy("MyConn")
        self.assertTrue(result)

    @patch('services.network.network.subprocess.run')
    def test_hostname_visible(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="ipv4.dhcp-send-hostname:yes\n"
        )
        result = NetworkUtils.check_hostname_privacy("MyConn")
        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="")
        result = NetworkUtils.check_hostname_privacy("MyConn")
        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_oserror_returns_none(self, mock_run):
        mock_run.side_effect = OSError("fail")
        result = NetworkUtils.check_hostname_privacy("MyConn")
        self.assertIsNone(result)

    @patch('services.network.network.subprocess.run')
    def test_timeout_returns_none(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 5)
        result = NetworkUtils.check_hostname_privacy("MyConn")
        self.assertIsNone(result)


class TestReactivateConnection(unittest.TestCase):
    """Tests for NetworkUtils.reactivate_connection()."""

    @patch('services.network.network.subprocess.run')
    def test_reactivate_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = NetworkUtils.reactivate_connection("MyConn")
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["nmcli", "con", "up", "MyConn"],
            capture_output=True,
            check=False,
            timeout=10,
        )

    @patch('services.network.network.subprocess.run')
    def test_reactivate_oserror(self, mock_run):
        mock_run.side_effect = OSError("fail")
        result = NetworkUtils.reactivate_connection("MyConn")
        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_reactivate_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("nmcli", 10)
        result = NetworkUtils.reactivate_connection("MyConn")
        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_reactivate_subprocess_error(self, mock_run):
        mock_run.side_effect = subprocess.SubprocessError("connection failed")
        result = NetworkUtils.reactivate_connection("MyConn")
        self.assertFalse(result)


class TestDaemonFirstNetworkMutations(unittest.TestCase):
    """Tests daemon-first behavior for network mutating methods."""

    @patch('services.network.network.subprocess.run')
    @patch('services.network.network.daemon_client.call_json')
    def test_connect_wifi_prefers_daemon_result(
        self,
        mock_call_json,
        mock_run,
    ):
        mock_call_json.return_value = True
        result = NetworkUtils.connect_wifi("MyWiFi")
        self.assertTrue(result)
        mock_call_json.assert_called_once_with("NetworkConnectWifi", "MyWiFi")
        mock_run.assert_not_called()

    @patch('services.network.network.subprocess.run')
    @patch('services.network.network.daemon_client.call_json')
    def test_connect_wifi_falls_back_local(self, mock_call_json, mock_run):
        mock_call_json.return_value = None
        mock_run.return_value = MagicMock(returncode=0)
        result = NetworkUtils.connect_wifi("MyWiFi")
        self.assertTrue(result)
        mock_call_json.assert_called_once_with("NetworkConnectWifi", "MyWiFi")
        mock_run.assert_called_once_with(
            ["nmcli", "device", "wifi", "connect", "MyWiFi"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

    @patch('services.network.network.subprocess.run')
    @patch('services.network.network.daemon_client.call_json')
    def test_apply_dns_prefers_daemon_result(self, mock_call_json, mock_run):
        mock_call_json.return_value = True
        result = NetworkUtils.apply_dns("Home", "auto")
        self.assertTrue(result)
        mock_call_json.assert_called_once_with(
            "NetworkApplyDns", "Home", "auto")
        mock_run.assert_not_called()

    @patch('services.network.network.subprocess.run')
    @patch('services.network.network.daemon_client.call_json')
    def test_set_hostname_privacy_prefers_daemon_result(
        self,
        mock_call_json,
        mock_run,
    ):
        mock_call_json.return_value = True
        result = NetworkUtils.set_hostname_privacy("Home", True)
        self.assertTrue(result)
        mock_call_json.assert_called_once_with(
            "NetworkSetHostnamePrivacy", "Home", True)
        mock_run.assert_not_called()


class TestNetworkLocalWriteReturnCodes(unittest.TestCase):
    """Tests strict local return semantics for network write paths."""

    @patch('services.network.network.subprocess.run')
    def test_connect_wifi_local_non_zero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=10)

        result = NetworkUtils.connect_wifi_local("MyWiFi")

        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_disconnect_wifi_local_non_zero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=4)

        result = NetworkUtils.disconnect_wifi_local("wlan0")

        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_apply_dns_local_non_zero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=2)

        result = NetworkUtils.apply_dns_local("Home", "1.1.1.1")

        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_set_hostname_privacy_local_non_zero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=5)

        result = NetworkUtils.set_hostname_privacy_local("Home", True)

        self.assertFalse(result)

    @patch('services.network.network.subprocess.run')
    def test_reactivate_connection_local_non_zero_returncode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)

        result = NetworkUtils.reactivate_connection_local("Home")

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
