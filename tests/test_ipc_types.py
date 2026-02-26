"""Tests for services.ipc.types payload guards."""

import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "loofi-fedora-tweaks"))

from services.ipc.types import (  # type: ignore[import-not-found]
    is_action_result_payload,
    is_package_payload,
    is_system_payload,
)


class TestIpcTypes(unittest.TestCase):
    """Validate fail-closed payload guards for daemon envelopes."""

    def test_action_result_payload_valid(self):
        self.assertTrue(is_action_result_payload({"success": True, "message": "ok"}))

    def test_action_result_payload_invalid(self):
        self.assertFalse(is_action_result_payload({"success": "yes", "message": "ok"}))

    def test_package_payload_rejects_unknown_package_method(self):
        self.assertFalse(is_package_payload("PackageUnknownMethod", {"success": True, "message": "ok"}))

    def test_package_payload_accepts_non_package_method_passthrough(self):
        self.assertTrue(is_package_payload("Ping", {"anything": "goes"}))

    def test_package_payload_boolean_path(self):
        self.assertTrue(is_package_payload("PackageIsInstalled", True))
        self.assertFalse(is_package_payload("PackageIsInstalled", "true"))

    def test_system_payload_rejects_unknown_system_method(self):
        self.assertFalse(is_system_payload("SystemUnknownMethod", {"success": True, "message": "ok"}))

    def test_system_payload_accepts_non_system_method_passthrough(self):
        self.assertTrue(is_system_payload("Ping", {"anything": "goes"}))

    def test_system_payload_known_type_paths(self):
        self.assertTrue(is_system_payload("SystemGetPackageManager", "dnf"))
        self.assertFalse(is_system_payload("SystemGetVariantName", {"name": "Workstation"}))
        self.assertTrue(is_system_payload("SystemHasPendingReboot", False))
        self.assertFalse(is_system_payload("SystemHasPendingReboot", "false"))
