"""Focused coverage tests for daemon handler modules."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "loofi-fedora-tweaks"))

from core.executor.action_result import ActionResult  # type: ignore[import-not-found]
from daemon.handlers.firewall_handler import FirewallHandler  # type: ignore[import-not-found]
from daemon.handlers.network_handler import NetworkHandler  # type: ignore[import-not-found]
from daemon.handlers.package_handler import PackageHandler  # type: ignore[import-not-found]
from daemon.handlers.service_handler import ServiceHandler  # type: ignore[import-not-found]
from services.system.services import UnitScope  # type: ignore[import-not-found]


class TestNetworkHandlerCoverage(unittest.TestCase):
    """Covers non-validation network handler paths."""

    @patch("daemon.handlers.network_handler.NetworkUtils")
    def test_scan_wifi_maps_rows(self, mock_utils):
        mock_utils.scan_wifi_local.return_value = [("ssid", "80%", "WPA2", "Connected")]
        rows = NetworkHandler.scan_wifi()
        self.assertEqual(rows[0]["ssid"], "ssid")

    @patch("daemon.handlers.network_handler.NetworkUtils")
    def test_load_vpn_connections_maps_rows(self, mock_utils):
        mock_utils.load_vpn_connections_local.return_value = [("vpn", "wireguard", "active")]
        rows = NetworkHandler.load_vpn_connections()
        self.assertEqual(rows[0]["name"], "vpn")

    @patch("daemon.handlers.network_handler.NetworkUtils")
    def test_detect_current_dns_returns_string(self, mock_utils):
        mock_utils.detect_current_dns_local.return_value = "1.1.1.1"
        self.assertEqual(NetworkHandler.detect_current_dns(), "1.1.1.1")

    @patch("daemon.handlers.network_handler.NetworkUtils")
    def test_get_active_connection_returns_empty_when_none(self, mock_utils):
        mock_utils.get_active_connection_local.return_value = None
        self.assertEqual(NetworkHandler.get_active_connection(), "")

    @patch("daemon.handlers.network_handler.NetworkUtils")
    def test_check_hostname_privacy_casts_to_bool(self, mock_utils):
        mock_utils.check_hostname_privacy_local.return_value = True
        self.assertTrue(NetworkHandler.check_hostname_privacy("wifi-home"))

    @patch("daemon.handlers.network_handler.NetworkUtils")
    def test_reactivate_connection_delegates(self, mock_utils):
        mock_utils.reactivate_connection_local.return_value = True
        self.assertTrue(NetworkHandler.reactivate_connection("wifi-home"))


class TestFirewallHandlerCoverage(unittest.TestCase):
    """Covers firewall read/write wrapper methods."""

    @patch("daemon.handlers.firewall_handler.FirewallManager")
    def test_get_status_serializes_dict(self, mock_manager):
        status = MagicMock()
        status.to_dict.return_value = {"running": True}
        mock_manager.get_status_local.return_value = status
        payload = FirewallHandler.get_status()
        self.assertTrue(payload["running"])

    @patch("daemon.handlers.firewall_handler.FirewallManager")
    def test_read_methods_delegate(self, mock_manager):
        mock_manager.list_ports_local.return_value = ["80/tcp"]
        mock_manager.list_services_local.return_value = ["ssh"]
        mock_manager.get_default_zone_local.return_value = "public"
        mock_manager.get_zones_local.return_value = ["public"]
        mock_manager.get_active_zones_local.return_value = {"public": ["eth0"]}
        mock_manager.list_rich_rules_local.return_value = ["rule"]

        self.assertEqual(FirewallHandler.list_ports(""), ["80/tcp"])
        self.assertEqual(FirewallHandler.list_services(""), ["ssh"])
        self.assertEqual(FirewallHandler.get_default_zone(), "public")
        self.assertEqual(FirewallHandler.get_zones(), ["public"])
        self.assertIn("public", FirewallHandler.get_active_zones())
        self.assertEqual(FirewallHandler.list_rich_rules(""), ["rule"])

    @patch("daemon.handlers.firewall_handler.FirewallManager")
    def test_set_default_zone_serializes_result(self, mock_manager):
        mock_manager.set_default_zone_local.return_value = MagicMock(success=True, message="ok")
        payload = FirewallHandler.set_default_zone("public")
        self.assertTrue(payload["success"])

    @patch("daemon.handlers.firewall_handler.PortAuditor")
    @patch("daemon.handlers.firewall_handler.FirewallManager")
    def test_start_stop_security_score_scan_ports(self, mock_manager, mock_auditor):
        mock_manager.start_firewall_local.return_value = MagicMock(success=True, message="started")
        mock_manager.stop_firewall_local.return_value = MagicMock(success=True, message="stopped")

        port_obj = MagicMock(protocol="tcp", port=22, address="0.0.0.0", process="sshd", pid=1, is_risky=False, risk_reason="")
        mock_auditor.scan_ports_local.return_value = [port_obj]
        mock_auditor.get_security_score_local.return_value = {"score": 90}

        self.assertTrue(FirewallHandler.start_firewall()["success"])
        self.assertTrue(FirewallHandler.stop_firewall()["success"])
        self.assertEqual(FirewallHandler.scan_ports()[0]["port"], 22)
        self.assertEqual(FirewallHandler.security_score()["score"], 90)

    @patch("daemon.handlers.firewall_handler.FirewallManager")
    def test_firewall_write_methods_delegate(self, mock_manager):
        mock_result = MagicMock(success=True, message="ok")
        mock_manager.add_service_local.return_value = mock_result
        mock_manager.remove_service_local.return_value = mock_result
        mock_manager.add_rich_rule_local.return_value = mock_result
        mock_manager.remove_rich_rule_local.return_value = mock_result
        mock_manager.open_port_local.return_value = mock_result
        mock_manager.close_port_local.return_value = mock_result

        self.assertTrue(FirewallHandler.add_service("ssh", "public", False)["success"])
        self.assertTrue(FirewallHandler.remove_service("ssh", "public", True)["success"])
        self.assertTrue(FirewallHandler.add_rich_rule("rule family=ipv4 service name=ssh accept", "public", True)["success"])
        self.assertTrue(FirewallHandler.remove_rich_rule("rule family=ipv4 service name=ssh accept", "public", False)["success"])
        self.assertTrue(FirewallHandler.open_port("80", "tcp", "public", True)["success"])
        self.assertTrue(FirewallHandler.close_port("443", "tcp", "public", False)["success"])

        mock_manager.add_service_local.assert_called_once_with("ssh", "public", permanent=False)
        mock_manager.remove_service_local.assert_called_once_with("ssh", "public", permanent=True)
        mock_manager.add_rich_rule_local.assert_called_once()
        mock_manager.remove_rich_rule_local.assert_called_once()
        mock_manager.open_port_local.assert_called_once_with("80", "tcp", "public", permanent=True)
        mock_manager.close_port_local.assert_called_once_with("443", "tcp", "public", permanent=False)


class TestPackageHandlerCoverage(unittest.TestCase):
    """Covers package handler dispatch and serialization branches."""

    @patch("daemon.handlers.package_handler.get_package_service")
    def test_install_remove_update_delegate_to_local_when_available(self, mock_get_service):
        service = MagicMock()
        service.install_local.return_value = ActionResult(success=True, message="ok")
        service.remove_local.return_value = ActionResult(success=True, message="ok")
        service.update_local.return_value = ActionResult(success=True, message="ok")
        mock_get_service.return_value = service

        self.assertTrue(PackageHandler.install(["vim"])["success"])
        self.assertTrue(PackageHandler.remove(["vim"])["success"])
        self.assertTrue(PackageHandler.update(["vim"])["success"])

    @patch("daemon.handlers.package_handler.get_package_service")
    def test_info_search_list_and_installed_paths(self, mock_get_service):
        service = MagicMock()
        service.search_local.return_value = ActionResult(success=True, message="ok")
        service.info_local.return_value = ActionResult(success=True, message="ok")
        service.list_installed_local.return_value = ActionResult(success=True, message="ok")
        service.is_installed_local.return_value = True
        mock_get_service.return_value = service

        self.assertTrue(PackageHandler.search("vim", limit=10)["success"])
        self.assertTrue(PackageHandler.info("vim")["success"])
        self.assertTrue(PackageHandler.list_installed()["success"])
        self.assertTrue(PackageHandler.is_installed("vim"))

    @patch("daemon.handlers.package_handler.get_package_service")
    def test_install_falls_back_to_non_local_when_local_missing(self, mock_get_service):
        service = MagicMock(spec=["install"])
        service.install.return_value = ActionResult(success=True, message="ok")
        mock_get_service.return_value = service

        payload = PackageHandler.install(["vim"])

        self.assertTrue(payload["success"])
        service.install.assert_called_once_with(["vim"])

    def test_serialize_result_handles_non_action_result(self):
        payload = PackageHandler._serialize_result(result=object())
        self.assertFalse(payload["success"])


class TestServiceHandlerCoverage(unittest.TestCase):
    """Covers remaining service handler wrapper methods."""

    @patch("daemon.handlers.service_handler.SystemService")
    def test_suspend_update_grub_set_hostname_delegate(self, mock_system_service):
        instance = mock_system_service.return_value
        instance.suspend_local.return_value = ActionResult(success=True, message="ok")
        instance.update_grub_local.return_value = ActionResult(success=True, message="ok")
        instance.set_hostname_local.return_value = ActionResult(success=True, message="ok")

        self.assertTrue(ServiceHandler.suspend("desc")["success"])
        self.assertTrue(ServiceHandler.update_grub("desc")["success"])
        self.assertTrue(ServiceHandler.set_hostname("fedora-workstation", "desc")["success"])

    @patch("daemon.handlers.service_handler.SystemManager")
    def test_static_system_queries(self, mock_system_manager):
        mock_system_manager.has_pending_deployment.return_value = True
        mock_system_manager.get_package_manager.return_value = "dnf"
        mock_system_manager.get_variant_name.return_value = "Workstation"

        self.assertTrue(ServiceHandler.has_pending_reboot())
        self.assertEqual(ServiceHandler.get_package_manager(), "dnf")
        self.assertEqual(ServiceHandler.get_variant_name(), "Workstation")

    @patch("daemon.handlers.service_handler.ServiceManager")
    def test_stop_restart_unit_delegate(self, mock_manager):
        mock_manager.stop_unit.return_value = MagicMock(success=True, message="stopped")
        mock_manager.restart_unit.return_value = MagicMock(success=True, message="restarted")

        stop_payload = ServiceHandler.stop_unit("sshd", "system")
        restart_payload = ServiceHandler.restart_unit("sshd", "user")

        self.assertTrue(stop_payload["success"])
        self.assertTrue(restart_payload["success"])
        mock_manager.stop_unit.assert_called_once_with("sshd", UnitScope.SYSTEM)
        mock_manager.restart_unit.assert_called_once_with("sshd", UnitScope.USER)

    def test_serialize_action_result_handles_non_action_result(self):
        payload = ServiceHandler._serialize_action_result(object())
        self.assertFalse(payload["success"])
