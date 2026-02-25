"""Tests for daemon contracts and server stubs."""

import json
import unittest
from unittest.mock import MagicMock, patch

from daemon.contracts import error_response, ok_response
from daemon.handlers.service_handler import ServiceHandler
from daemon.server import DaemonServiceBase
from daemon.validators import ValidationError, validate_port, validate_protocol, validate_zone
from services.system.services import ServiceUnit, UnitScope, UnitState
from core.executor.action_result import ActionResult


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

