"""Tests for services.ipc.daemon_client."""

import os
import unittest
from unittest.mock import patch

from services.ipc.daemon_client import DaemonClient
from services.ipc.errors import DaemonExecutionError, DaemonRequiredModeError, DaemonValidationError


class TestDaemonClient(unittest.TestCase):
    """DaemonClient behavior and envelope parsing tests."""

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "disabled"})
    def test_call_json_returns_none_when_disabled(self):
        client = DaemonClient()
        self.assertIsNone(client.call_json("Ping"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_call_json_returns_data_on_success(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {"value": 42}, "error": null}'
        client = DaemonClient()
        self.assertEqual(client.call_json("Ping"), {"value": 42})

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_call_json_raises_validation_error(self, mock_raw):
        mock_raw.return_value = '{"ok": false, "data": null, "error": {"code":"validation_error","message":"bad"}}'
        client = DaemonClient()
        with self.assertRaises(DaemonValidationError):
            client.call_json("Ping")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_call_json_raises_execution_error(self, mock_raw):
        mock_raw.return_value = '{"ok": false, "data": null, "error": {"code":"execution_error","message":"boom"}}'
        client = DaemonClient()
        with self.assertRaises(DaemonExecutionError):
            client.call_json("Ping")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_non_object_envelope(self, mock_raw):
        mock_raw.return_value = '["not", "an", "envelope"]'
        client = DaemonClient()
        self.assertIsNone(client.call_json("Ping"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_non_boolean_ok(self, mock_raw):
        mock_raw.return_value = '{"ok": "yes", "data": {}, "error": null}'
        client = DaemonClient()
        self.assertIsNone(client.call_json("Ping"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_invalid_error_shape(self, mock_raw):
        mock_raw.return_value = '{"ok": false, "data": null, "error": "boom"}'
        client = DaemonClient()
        self.assertIsNone(client.call_json("Ping"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "required"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_required_mode_raises_on_non_object_envelope(self, mock_raw):
        mock_raw.return_value = '["not", "an", "envelope"]'
        client = DaemonClient()
        with self.assertRaises(DaemonRequiredModeError):
            client.call_json("Ping")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_malformed_package_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {"value": 42}, "error": null}'
        client = DaemonClient()
        self.assertIsNone(client.call_json("PackageInfo", "vim"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "required"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_required_mode_raises_on_malformed_package_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {"value": 42}, "error": null}'
        client = DaemonClient()
        with self.assertRaises(DaemonRequiredModeError):
            client.call_json("PackageInfo", "vim")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_malformed_system_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {"value": 42}, "error": null}'
        client = DaemonClient()
        self.assertIsNone(client.call_json("SystemGetPackageManager"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "required"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_required_mode_raises_on_malformed_system_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {"value": 42}, "error": null}'
        client = DaemonClient()
        with self.assertRaises(DaemonRequiredModeError):
            client.call_json("SystemGetVariantName")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_call_json_returns_string_on_valid_system_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": "dnf", "error": null}'
        client = DaemonClient()
        self.assertEqual(client.call_json("SystemGetPackageManager"), "dnf")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_call_json_returns_bool_on_valid_system_reboot_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": true, "error": null}'
        client = DaemonClient()
        self.assertTrue(client.call_json("SystemHasPendingReboot"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_malformed_package_list_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": true, "error": null}'
        client = DaemonClient()
        self.assertIsNone(client.call_json("PackageListInstalled"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_preferred_mode_falls_back_on_unknown_package_method_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {}, "error": null}'
        client = DaemonClient()
        self.assertIsNone(client.call_json("PackageUnknownMethod"))

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "required"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_required_mode_raises_on_unknown_system_method_payload(self, mock_raw):
        mock_raw.return_value = '{"ok": true, "data": {}, "error": null}'
        client = DaemonClient()
        with self.assertRaises(DaemonRequiredModeError):
            client.call_json("SystemUnknownMethod")
