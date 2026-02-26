"""Tests for daemon contracts and server stubs."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from core.executor.action_result import ActionResult
from daemon.contracts import error_response, ok_response
from daemon.handlers.firewall_handler import FirewallHandler
from daemon.handlers.network_handler import NetworkHandler
from daemon.handlers.package_handler import PackageHandler
from daemon.handlers.service_handler import ServiceHandler
from daemon.server import DaemonServiceBase
from daemon.validators import (
    ValidationError,
    build_policy_inventory,
    build_validator_coverage_map,
    validate_port,
    validate_protocol,
    validate_zone,
)
from services.system.services import ServiceUnit, UnitScope, UnitState


class TestDaemonDBusContracts(unittest.TestCase):
    """Validate daemon envelopes and basic server behavior."""

    def test_ok_response_serialization(self):
        payload = ok_response({"hello": "world"})
        parsed = json.loads(payload)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["data"]["hello"], "world")
        self.assertIsNone(parsed["error"])

    def test_error_response_serialization(self):
        payload = error_response("validation_error", "bad input")
        parsed = json.loads(payload)
        self.assertFalse(parsed["ok"])
        self.assertEqual(parsed["error"]["code"], "validation_error")

    def test_ping_base_service(self):
        svc = DaemonServiceBase()
        parsed = json.loads(svc.Ping())
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["data"], "pong")

    def test_validators_reject_bad_values(self):
        with self.assertRaises(ValidationError):
            validate_port("99999")
        with self.assertRaises(ValidationError):
            validate_protocol("icmp")
        with self.assertRaises(ValidationError):
            validate_zone("../root")


class TestServiceHandler(unittest.TestCase):
    """Validate service handler serialization and scope parsing."""

    @patch("daemon.handlers.service_handler.SystemService")
    def test_reboot_serializes_action_result(self, mock_system_service):
        instance = mock_system_service.return_value
        instance.reboot_local.return_value = ActionResult(success=True, message="ok", exit_code=0)

        payload = ServiceHandler.reboot(description="reboot", delay_seconds=5)

        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "ok")
        instance.reboot_local.assert_called_once_with(description="reboot", delay_seconds=5)

    @patch("daemon.handlers.service_handler.ServiceManager")
    def test_list_units_maps_units_to_dicts(self, mock_service_manager):
        mock_service_manager.list_units.return_value = [
            ServiceUnit(
                name="gamemoded",
                state=UnitState.ACTIVE,
                scope=UnitScope.USER,
                description="GameMode daemon",
                is_gaming=True,
            )
        ]

        payload = ServiceHandler.list_units(scope="user", filter_type="gaming")

        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["name"], "gamemoded")
        self.assertEqual(payload[0]["state"], "active")
        self.assertEqual(payload[0]["scope"], "user")
        self.assertTrue(payload[0]["is_gaming"])

    @patch("daemon.handlers.service_handler.ServiceManager")
    def test_start_unit_uses_system_scope_when_requested(self, mock_service_manager):
        mock_service_manager.start_unit.return_value = MagicMock(success=True, message="Started sshd")

        payload = ServiceHandler.start_unit("sshd", scope="system")

        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "Started sshd")
        mock_service_manager.start_unit.assert_called_once_with("sshd", UnitScope.SYSTEM)

    def test_reboot_rejects_negative_delay(self):
        with self.assertRaises(ValidationError):
            ServiceHandler.reboot(delay_seconds=-1)

    def test_list_units_rejects_invalid_scope(self):
        with self.assertRaises(ValidationError):
            ServiceHandler.list_units(scope="kernel")


class TestHandlerValidatorTightening(unittest.TestCase):
    """Validate deny-by-default hardening in prioritized handler pathways."""

    def test_network_connect_wifi_rejects_blank_ssid(self):
        with self.assertRaises(ValidationError):
            NetworkHandler.connect_wifi("  ")

    def test_network_set_hostname_privacy_rejects_non_boolean(self):
        with self.assertRaises(ValidationError):
            NetworkHandler.set_hostname_privacy("wifi-home", "true")

    def test_firewall_add_service_rejects_invalid_service_name(self):
        with self.assertRaises(ValidationError):
            FirewallHandler.add_service("../../ssh")

    def test_firewall_add_rich_rule_rejects_newline_payload(self):
        with self.assertRaises(ValidationError):
            FirewallHandler.add_rich_rule("rule family=ipv4\nsource address=1.2.3.4")

    def test_package_install_rejects_empty_package_list(self):
        with self.assertRaises(ValidationError):
            PackageHandler.install([])

    def test_package_search_rejects_invalid_limit(self):
        with self.assertRaises(ValidationError):
            PackageHandler.search("vim", limit=0)


class TestPolicyInventory(unittest.TestCase):
    """Validate policy inventory extraction."""

    def test_build_policy_inventory_reads_repo_policies(self):
        entries = build_policy_inventory()

        self.assertGreater(len(entries), 0)
        action_ids = {entry["action_id"] for entry in entries}
        self.assertIn("org.loofi.fedora-tweaks.service-manage", action_ids)

        service_entry = next(entry for entry in entries if entry["action_id"] == "org.loofi.fedora-tweaks.service-manage")
        self.assertEqual(service_entry["allow_active"], "auth_admin")
        self.assertEqual(service_entry["policy_file"], "org.loofi.fedora-tweaks.service-manage.policy")

    def test_build_policy_inventory_skips_invalid_xml(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            invalid = temp_path / "org.loofi.fedora-tweaks.invalid.policy"
            invalid.write_text("<policyconfig><action>", encoding="utf-8")

            entries = build_policy_inventory(temp_path)

        self.assertEqual(entries, [])


class TestValidatorCoverageMap(unittest.TestCase):
    """Validate handler-to-validator coverage mapping."""

    def test_build_validator_coverage_map_finds_handlers(self):
        rows = build_validator_coverage_map()

        self.assertGreater(len(rows), 0)
        handlers = {row["handler"] for row in rows}
        self.assertIn("FirewallHandler", handlers)
        self.assertIn("NetworkHandler", handlers)

    def test_build_validator_coverage_map_reports_validated_params(self):
        rows = build_validator_coverage_map()

        open_port = next(
            row
            for row in rows
            if row["handler"] == "FirewallHandler" and row["method"] == "open_port"
        )

        self.assertIn("validate_port", open_port["validator_calls"])
        self.assertIn("validate_protocol", open_port["validator_calls"])
        self.assertIn("validate_zone", open_port["validator_calls"])
        self.assertIn("port", open_port["validated_parameters"])
        self.assertIn("protocol", open_port["validated_parameters"])
        self.assertIn("zone", open_port["validated_parameters"])

    def test_build_validator_coverage_map_reports_gaps(self):
        rows = build_validator_coverage_map()

        connect_wifi = next(
            row
            for row in rows
            if row["handler"] == "NetworkHandler" and row["method"] == "connect_wifi"
        )

        self.assertIn("validate_ssid", connect_wifi["validator_calls"])
        self.assertNotIn("ssid", connect_wifi["unvalidated_parameters"])














