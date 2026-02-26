"""Tests for daemon.validators hardening helpers."""

import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "loofi-fedora-tweaks"))

from daemon.validators import (  # type: ignore[import-not-found]
    ValidationError,
    validate_boolean,
    validate_delay_seconds,
    validate_dns_servers,
    validate_firewall_service,
    validate_hostname,
    validate_interface_name,
    validate_package_list,
    validate_package_name,
    validate_rich_rule,
    validate_search_limit,
    validate_search_query,
    validate_ssid,
    validate_unit_filter,
    validate_unit_name,
    validate_unit_scope,
)


class TestDaemonValidators(unittest.TestCase):
    """Validate deny-by-default helper behavior for daemon input validation."""

    def test_validate_ssid_accepts_valid_name(self):
        self.assertEqual(validate_ssid("HomeWiFi"), "HomeWiFi")

    def test_validate_ssid_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_ssid("  ")

    def test_validate_interface_name_accepts(self):
        self.assertEqual(validate_interface_name("wlan0"), "wlan0")

    def test_validate_interface_name_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_interface_name("../../eth0")

    def test_validate_dns_servers_accepts_auto(self):
        self.assertEqual(validate_dns_servers("auto"), "auto")

    def test_validate_dns_servers_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_dns_servers("1.1.1.1; rm -rf /")

    def test_validate_firewall_service_accepts(self):
        self.assertEqual(validate_firewall_service("ssh"), "ssh")

    def test_validate_firewall_service_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_firewall_service("../ssh")

    def test_validate_rich_rule_accepts(self):
        rule = 'rule family="ipv4" source address="1.2.3.4" service name="ssh" accept'
        self.assertEqual(validate_rich_rule(rule), rule)

    def test_validate_rich_rule_rejects_multiline(self):
        with self.assertRaises(ValidationError):
            validate_rich_rule("rule family=ipv4\naccept")

    def test_validate_boolean_accepts_bool(self):
        self.assertTrue(validate_boolean(True, "permanent"))

    def test_validate_boolean_rejects_non_bool(self):
        with self.assertRaises(ValidationError):
            validate_boolean("true", "permanent")

    def test_validate_unit_scope_accepts(self):
        self.assertEqual(validate_unit_scope("system"), "system")

    def test_validate_unit_scope_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_unit_scope("kernel")

    def test_validate_unit_filter_accepts(self):
        self.assertEqual(validate_unit_filter("failed"), "failed")

    def test_validate_unit_filter_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_unit_filter("pending")

    def test_validate_unit_name_accepts_service_suffix(self):
        self.assertEqual(validate_unit_name("sshd.service"), "sshd")

    def test_validate_unit_name_rejects_path_chars(self):
        with self.assertRaises(ValidationError):
            validate_unit_name("../../sshd")

    def test_validate_delay_seconds_accepts_int(self):
        self.assertEqual(validate_delay_seconds(30), 30)

    def test_validate_delay_seconds_rejects_negative(self):
        with self.assertRaises(ValidationError):
            validate_delay_seconds(-1)

    def test_validate_hostname_accepts(self):
        self.assertEqual(validate_hostname("fedora-workstation"), "fedora-workstation")

    def test_validate_hostname_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_hostname("bad host")

    def test_validate_package_name_accepts(self):
        self.assertEqual(validate_package_name("vim-enhanced"), "vim-enhanced")

    def test_validate_package_name_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            validate_package_name("vim;rm")

    def test_validate_package_list_accepts(self):
        self.assertEqual(validate_package_list(["vim", "git"]), ["vim", "git"])

    def test_validate_package_list_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_package_list([])

    def test_validate_search_query_accepts(self):
        self.assertEqual(validate_search_query("mesa"), "mesa")

    def test_validate_search_query_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_search_query("  ")

    def test_validate_search_limit_accepts(self):
        self.assertEqual(validate_search_limit(50), 50)

    def test_validate_search_limit_rejects_zero(self):
        with self.assertRaises(ValidationError):
            validate_search_limit(0)
