"""Tests for IPC mode fallback semantics."""

import os
import unittest
from unittest.mock import patch

from services.ipc.daemon_client import DaemonClient
from services.ipc.errors import DaemonRequiredModeError
from services.network.network import NetworkUtils
from services.package.service import DnfPackageService
from services.system.service import SystemService


class TestIPCFallbackModes(unittest.TestCase):
    """Validate disabled/preferred/required behavior."""

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.network.network.daemon_client.call_json")
    @patch("services.network.network.NetworkUtils.scan_wifi_local")
    def test_preferred_falls_back_to_local(self, mock_local, mock_call):
        mock_call.return_value = None
        mock_local.return_value = [("ssid", "80%", "WPA2", "Connected")]
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows, [("ssid", "80%", "WPA2", "Connected")])

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "disabled"})
    @patch("services.network.network.daemon_client.call_json")
    @patch("services.network.network.NetworkUtils.scan_wifi_local")
    def test_disabled_uses_local_only(self, mock_local, mock_call):
        mock_call.return_value = None
        mock_local.return_value = [("ssid2", "50%", "Open", "")]
        rows = NetworkUtils.scan_wifi()
        self.assertEqual(rows[0][0], "ssid2")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.network.network.daemon_client.call_json")
    @patch("services.network.network.NetworkUtils.get_active_connection_local")
    def test_preferred_active_connection_falls_back_to_local(self, mock_local, mock_call):
        mock_call.return_value = None
        mock_local.return_value = "Home"

        conn = NetworkUtils.get_active_connection()

        self.assertEqual(conn, "Home")
        mock_local.assert_called_once_with()

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.network.network.daemon_client.call_json")
    @patch("services.network.network.NetworkUtils.get_active_connection_local")
    def test_preferred_active_connection_local_none_stays_none(self, mock_local, mock_call):
        mock_call.return_value = None
        mock_local.return_value = None

        conn = NetworkUtils.get_active_connection()

        self.assertIsNone(conn)
        mock_local.assert_called_once_with()

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "required"})
    @patch("services.ipc.daemon_client.DaemonClient._call_raw")
    def test_required_mode_raises_on_transport_error(self, mock_raw):
        mock_raw.side_effect = RuntimeError("no bus")
        client = DaemonClient()
        with self.assertRaises(DaemonRequiredModeError):
            client.call_json("Ping")

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.package.service.daemon_client.call_json")
    @patch("services.package.service.CommandWorker")
    def test_preferred_package_install_falls_back_to_local(self, mock_worker_class, mock_call):
        mock_call.return_value = None
        mock_worker = mock_worker_class.return_value
        mock_worker.get_result.return_value.success = True
        mock_worker.get_result.return_value.message = "ok"

        result = DnfPackageService().install(["vim"])

        self.assertTrue(result.success)
        mock_worker_class.assert_called_once()

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.package.service.daemon_client.call_json")
    @patch("services.package.service.CommandWorker")
    def test_preferred_package_update_falls_back_to_local(
        self,
        mock_worker_class,
        mock_call,
    ):
        mock_call.return_value = None
        mock_worker = mock_worker_class.return_value
        mock_worker.get_result.return_value.success = True
        mock_worker.get_result.return_value.message = "ok"

        result = DnfPackageService().update(["vim"])

        self.assertTrue(result.success)
        mock_worker_class.assert_called_once()

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "disabled"})
    @patch("services.package.service.daemon_client.call_json")
    @patch("services.package.service.CommandWorker")
    def test_disabled_package_install_uses_local_path(self, mock_worker_class, mock_call):
        mock_call.return_value = None
        mock_worker = mock_worker_class.return_value
        mock_worker.get_result.return_value.success = True
        mock_worker.get_result.return_value.message = "ok"

        result = DnfPackageService().install(["git"])

        self.assertTrue(result.success)
        mock_worker_class.assert_called_once()

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "preferred"})
    @patch("services.system.service.daemon_client.call_json")
    @patch("services.system.service.CommandWorker")
    def test_preferred_system_reboot_falls_back_to_local(self, mock_worker_class, mock_call):
        mock_call.return_value = None
        mock_worker = mock_worker_class.return_value
        mock_worker.get_result.return_value.success = True
        mock_worker.get_result.return_value.message = "ok"

        result = SystemService().reboot()

        self.assertTrue(result.success)
        mock_worker_class.assert_called_once()

    @patch.dict(os.environ, {"LOOFI_IPC_MODE": "disabled"})
    @patch("services.system.service.daemon_client.call_json")
    @patch("services.system.service.CommandWorker")
    def test_disabled_system_reboot_uses_local_path(self, mock_worker_class, mock_call):
        mock_call.return_value = None
        mock_worker = mock_worker_class.return_value
        mock_worker.get_result.return_value.success = True
        mock_worker.get_result.return_value.message = "ok"

        result = SystemService().reboot()

        self.assertTrue(result.success)
        mock_worker_class.assert_called_once()
