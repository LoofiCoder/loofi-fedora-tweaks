"""Tests for services.desktop.* modules.

Covers DesktopManager, DisplayManager, and KWinManager classes.
DesktopUtils.detect_color_scheme is already tested in test_desktop_utils.py.
"""

import os
import subprocess
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))

from services.desktop.display import WaylandDisplayManager, DisplayInfo
from services.desktop.kwin import KWinManager, Result


# ====================================================================================
# WaylandDisplayManager Tests
# ====================================================================================


class TestIsWayland(unittest.TestCase):
    """Tests for WaylandDisplayManager.is_wayland()."""

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"})
    def test_is_wayland_true(self):
        """Wayland session is detected."""
        self.assertTrue(WaylandDisplayManager.is_wayland())

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11"})
    def test_is_wayland_false_x11(self):
        """X11 session returns False."""
        self.assertFalse(WaylandDisplayManager.is_wayland())

    @patch.dict(os.environ, {}, clear=True)
    def test_is_wayland_false_missing(self):
        """Missing XDG_SESSION_TYPE returns False."""
        self.assertFalse(WaylandDisplayManager.is_wayland())


class TestDetectDE(unittest.TestCase):
    """Tests for WaylandDisplayManager._detect_de()."""

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "GNOME"})
    def test_detect_gnome(self):
        """GNOME desktop is detected."""
        self.assertEqual(WaylandDisplayManager._detect_de(), "gnome")

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "KDE"})
    def test_detect_kde(self):
        """KDE desktop is detected."""
        self.assertEqual(WaylandDisplayManager._detect_de(), "kde")

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "plasma"})
    def test_detect_plasma(self):
        """Plasma desktop is detected as KDE."""
        self.assertEqual(WaylandDisplayManager._detect_de(), "kde")

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "XFCE"})
    def test_detect_unknown(self):
        """Unknown desktop returns 'unknown'."""
        self.assertEqual(WaylandDisplayManager._detect_de(), "unknown")

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_missing(self):
        """Missing XDG_CURRENT_DESKTOP returns 'unknown'."""
        self.assertEqual(WaylandDisplayManager._detect_de(), "unknown")


class TestGetDisplays(unittest.TestCase):
    """Tests for WaylandDisplayManager.get_displays()."""

    @patch('services.desktop.display.WaylandDisplayManager.is_wayland', return_value=False)
    @patch('services.desktop.display.WaylandDisplayManager._get_displays_xrandr', return_value=[])
    def test_non_wayland_uses_xrandr(self, mock_xrandr, mock_is_wayland):
        """Non-Wayland session attempts xrandr fallback."""
        result = WaylandDisplayManager.get_displays()
        self.assertEqual(result, [])
        mock_xrandr.assert_called_once()

    @patch('services.desktop.display.WaylandDisplayManager.is_wayland', return_value=True)
    @patch('services.desktop.display.WaylandDisplayManager._detect_de', return_value='gnome')
    @patch('services.desktop.display.WaylandDisplayManager._get_displays_gnome', return_value=[DisplayInfo(name="eDP-1")])
    def test_gnome_wayland(self, mock_gnome, mock_de, mock_is_wayland):
        """GNOME Wayland session uses GNOME display getter."""
        result = WaylandDisplayManager.get_displays()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "eDP-1")
        mock_gnome.assert_called_once()

    @patch('services.desktop.display.WaylandDisplayManager.is_wayland', return_value=True)
    @patch('services.desktop.display.WaylandDisplayManager._detect_de', return_value='kde')
    @patch('services.desktop.display.WaylandDisplayManager._get_displays_kde', return_value=[DisplayInfo(name="HDMI-1")])
    def test_kde_wayland(self, mock_kde, mock_de, mock_is_wayland):
        """KDE Wayland session uses KDE display getter."""
        result = WaylandDisplayManager.get_displays()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "HDMI-1")
        mock_kde.assert_called_once()

    @patch('services.desktop.display.WaylandDisplayManager.is_wayland', return_value=True)
    @patch('services.desktop.display.WaylandDisplayManager._detect_de', return_value='unknown')
    def test_unknown_de_wayland(self, mock_de, mock_is_wayland):
        """Unknown desktop returns empty list."""
        result = WaylandDisplayManager.get_displays()
        self.assertEqual(result, [])


class TestGetDisplaysGNOME(unittest.TestCase):
    """Tests for WaylandDisplayManager._get_displays_gnome()."""

    @patch('services.desktop.display.subprocess.run')
    def test_gnome_success(self, mock_run):
        """GNOME display enumeration succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stdout="eDP-1\n1920x1080\nprimary\n")
        result = WaylandDisplayManager._get_displays_gnome()
        self.assertIsInstance(result, list)

    @patch('services.desktop.display.subprocess.run')
    def test_gnome_timeout(self, mock_run):
        """GNOME display enumeration handles timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='gnome-monitor-config', timeout=10)
        result = WaylandDisplayManager._get_displays_gnome()
        self.assertEqual(result, [])

    @patch('services.desktop.display.subprocess.run')
    def test_gnome_not_found(self, mock_run):
        """GNOME display enumeration handles missing tool."""
        mock_run.side_effect = FileNotFoundError
        result = WaylandDisplayManager._get_displays_gnome()
        self.assertEqual(result, [])


class TestGetDisplaysKDE(unittest.TestCase):
    """Tests for WaylandDisplayManager._get_displays_kde()."""

    @patch('services.desktop.display.cached_which', return_value=None)
    def test_kscreen_doctor_not_found(self, mock_which):
        """KDE display enumeration handles missing tool."""
        result = WaylandDisplayManager._get_displays_kde()
        self.assertEqual(result, [])

    @patch('services.desktop.display.cached_which', return_value='/usr/bin/kscreen-doctor')
    @patch('services.desktop.display.subprocess.run')
    def test_kde_success(self, mock_run, mock_which):
        """KDE display enumeration succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Output: 1\nName: HDMI-1\nEnabled: true\n")
        result = WaylandDisplayManager._get_displays_kde()
        self.assertIsInstance(result, list)

    @patch('services.desktop.display.cached_which', return_value='/usr/bin/kscreen-doctor')
    @patch('services.desktop.display.subprocess.run')
    def test_kde_timeout(self, mock_run, mock_which):
        """KDE display enumeration handles timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='kscreen-doctor', timeout=10)
        result = WaylandDisplayManager._get_displays_kde()
        self.assertEqual(result, [])


class TestGetDisplaysXrandr(unittest.TestCase):
    """Tests for WaylandDisplayManager._get_displays_xrandr()."""

    @patch('services.desktop.display.cached_which', return_value=None)
    def test_xrandr_not_found(self, mock_which):
        """xrandr fallback handles missing tool."""
        result = WaylandDisplayManager._get_displays_xrandr()
        self.assertEqual(result, [])

    @patch('services.desktop.display.cached_which', return_value='/usr/bin/xrandr')
    @patch('services.desktop.display.subprocess.run')
    def test_xrandr_success(self, mock_run, mock_which):
        """xrandr fallback succeeds."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="HDMI-1 connected primary 1920x1080+0+0\neDP-1 connected 1366x768+1920+0\n"
        )
        result = WaylandDisplayManager._get_displays_xrandr()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "HDMI-1")
        self.assertTrue(result[0].primary)

    @patch('services.desktop.display.cached_which', return_value='/usr/bin/xrandr')
    @patch('services.desktop.display.subprocess.run')
    def test_xrandr_timeout(self, mock_run, mock_which):
        """xrandr fallback handles timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='xrandr', timeout=10)
        result = WaylandDisplayManager._get_displays_xrandr()
        self.assertEqual(result, [])


class TestSetScaling(unittest.TestCase):
    """Tests for WaylandDisplayManager.set_scaling()."""

    @patch('services.desktop.display.WaylandDisplayManager._detect_de', return_value='gnome')
    def test_set_scaling_gnome(self, mock_de):
        """GNOME scaling returns gsettings command."""
        binary, args, desc = WaylandDisplayManager.set_scaling("eDP-1", 1.5)
        self.assertEqual(binary, "gsettings")
        self.assertIn("text-scaling-factor", args)

    @patch('services.desktop.display.WaylandDisplayManager._detect_de', return_value='kde')
    @patch('services.desktop.display.cached_which', return_value='/usr/bin/kscreen-doctor')
    def test_set_scaling_kde(self, mock_which, mock_de):
        """KDE scaling returns kscreen-doctor command."""
        binary, args, desc = WaylandDisplayManager.set_scaling("HDMI-1", 2.0)
        self.assertEqual(binary, "kscreen-doctor")
        self.assertIn("output.HDMI-1.scale.2.0", args)

    @patch('services.desktop.display.WaylandDisplayManager._detect_de', return_value='unknown')
    def test_set_scaling_unknown_de(self, mock_de):
        """Unknown DE returns echo fallback."""
        binary, args, desc = WaylandDisplayManager.set_scaling("eDP-1", 1.0)
        self.assertEqual(binary, "echo")


# ====================================================================================
# KWinManager Tests
# ====================================================================================


class TestIsKDE(unittest.TestCase):
    """Tests for KWinManager.is_kde()."""

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "KDE"})
    def test_is_kde_true_kde(self):
        """KDE desktop detected."""
        self.assertTrue(KWinManager.is_kde())

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "plasma"})
    def test_is_kde_true_plasma(self):
        """Plasma desktop detected as KDE."""
        self.assertTrue(KWinManager.is_kde())

    @patch.dict(os.environ, {"XDG_CURRENT_DESKTOP": "GNOME"})
    def test_is_kde_false(self):
        """Non-KDE desktop returns False."""
        self.assertFalse(KWinManager.is_kde())


class TestIsKDEWayland(unittest.TestCase):
    """Tests for KWinManager.is_wayland()."""

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"})
    def test_is_wayland_true(self):
        """Wayland session detected."""
        self.assertTrue(KWinManager.is_wayland())

    @patch.dict(os.environ, {"XDG_SESSION_TYPE": "x11"})
    def test_is_wayland_false(self):
        """X11 session returns False."""
        self.assertFalse(KWinManager.is_wayland())


class TestGetKwriteconfig(unittest.TestCase):
    """Tests for KWinManager.get_kwriteconfig()."""

    @patch('services.desktop.kwin.cached_which')
    def test_kwriteconfig6_found(self, mock_which):
        """kwriteconfig6 is preferred."""
        mock_which.side_effect = lambda cmd: "/usr/bin/kwriteconfig6" if cmd == "kwriteconfig6" else None
        result = KWinManager.get_kwriteconfig()
        self.assertEqual(result, "kwriteconfig6")

    @patch('services.desktop.kwin.cached_which')
    def test_kwriteconfig5_fallback(self, mock_which):
        """kwriteconfig5 is fallback."""
        mock_which.side_effect = lambda cmd: "/usr/bin/kwriteconfig5" if cmd == "kwriteconfig5" else None
        result = KWinManager.get_kwriteconfig()
        self.assertEqual(result, "kwriteconfig5")

    @patch('services.desktop.kwin.cached_which', return_value=None)
    def test_kwriteconfig_not_found(self, mock_which):
        """Neither version found returns None."""
        result = KWinManager.get_kwriteconfig()
        self.assertIsNone(result)


class TestGetKreadconfig(unittest.TestCase):
    """Tests for KWinManager.get_kreadconfig()."""

    @patch('services.desktop.kwin.cached_which')
    def test_kreadconfig6_found(self, mock_which):
        """kreadconfig6 is preferred."""
        mock_which.side_effect = lambda cmd: "/usr/bin/kreadconfig6" if cmd == "kreadconfig6" else None
        result = KWinManager.get_kreadconfig()
        self.assertEqual(result, "kreadconfig6")

    @patch('services.desktop.kwin.cached_which')
    def test_kreadconfig5_fallback(self, mock_which):
        """kreadconfig5 is fallback."""
        mock_which.side_effect = lambda cmd: "/usr/bin/kreadconfig5" if cmd == "kreadconfig5" else None
        result = KWinManager.get_kreadconfig()
        self.assertEqual(result, "kreadconfig5")

    @patch('services.desktop.kwin.cached_which', return_value=None)
    def test_kreadconfig_not_found(self, mock_which):
        """Neither version found returns None."""
        result = KWinManager.get_kreadconfig()
        self.assertIsNone(result)


class TestEnableQuickTiling(unittest.TestCase):
    """Tests for KWinManager.enable_quick_tiling()."""

    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value=None)
    def test_enable_quick_tiling_no_tool(self, mock_kwrite):
        """Enable quick tiling fails when kwriteconfig not found."""
        result = KWinManager.enable_quick_tiling()
        self.assertFalse(result.success)
        self.assertIn("not found", result.message)

    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value='kwriteconfig6')
    @patch('services.desktop.kwin.subprocess.run')
    def test_enable_quick_tiling_success(self, mock_run, mock_kwrite):
        """Enable quick tiling succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = KWinManager.enable_quick_tiling()
        self.assertTrue(result.success)
        self.assertIn("enabled", result.message.lower())

    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value='kwriteconfig6')
    @patch('services.desktop.kwin.subprocess.run')
    def test_enable_quick_tiling_failure(self, mock_run, mock_kwrite):
        """Enable quick tiling handles subprocess failure."""
        mock_run.return_value = MagicMock(returncode=1, stderr="failed")
        result = KWinManager.enable_quick_tiling()
        self.assertFalse(result.success)

    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value='kwriteconfig6')
    @patch('services.desktop.kwin.subprocess.run')
    def test_enable_quick_tiling_exception(self, mock_run, mock_kwrite):
        """Enable quick tiling handles exception."""
        mock_run.side_effect = OSError("boom")
        result = KWinManager.enable_quick_tiling()
        self.assertFalse(result.success)
        self.assertIn("Error", result.message)


class TestSetKeybinding(unittest.TestCase):
    """Tests for KWinManager.set_keybinding()."""

    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value=None)
    def test_set_keybinding_no_tool(self, mock_kwrite):
        """Set keybinding fails when kwriteconfig not found."""
        result = KWinManager.set_keybinding("Meta+H", "left")
        self.assertFalse(result.success)

    def test_set_keybinding_unknown_action(self):
        """Set keybinding rejects unknown action."""
        result = KWinManager.set_keybinding("Meta+X", "invalid_action")
        self.assertFalse(result.success)
        self.assertIn("Unknown action", result.message)

    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value='kwriteconfig6')
    @patch('services.desktop.kwin.subprocess.run')
    def test_set_keybinding_success(self, mock_run, mock_kwrite):
        """Set keybinding succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        result = KWinManager.set_keybinding("Meta+H", "left")
        self.assertTrue(result.success)
        self.assertIn("Bound", result.message)


class TestApplyTilingPreset(unittest.TestCase):
    """Tests for KWinManager.apply_tiling_preset()."""

    @patch('services.desktop.kwin.KWinManager.set_keybinding')
    def test_apply_vim_preset(self, mock_set):
        """Apply vim preset sets all bindings."""
        mock_set.return_value = Result(True, "ok")
        result = KWinManager.apply_tiling_preset("vim")
        self.assertTrue(result.success)
        self.assertIn("vim", result.message.lower())
        self.assertGreater(mock_set.call_count, 5)

    @patch('services.desktop.kwin.KWinManager.set_keybinding')
    def test_apply_arrows_preset(self, mock_set):
        """Apply arrows preset sets all bindings."""
        mock_set.return_value = Result(True, "ok")
        result = KWinManager.apply_tiling_preset("arrows")
        self.assertTrue(result.success)
        self.assertIn("arrows", result.message.lower())

    def test_apply_unknown_preset(self):
        """Apply unknown preset returns error."""
        result = KWinManager.apply_tiling_preset("invalid")
        self.assertFalse(result.success)
        self.assertIn("Unknown preset", result.message)

    @patch('services.desktop.kwin.KWinManager.set_keybinding')
    def test_apply_preset_partial_failure(self, mock_set):
        """Apply preset handles partial failures."""
        # vim preset has 9 bindings
        mock_set.side_effect = [
            Result(True, "ok"),
            Result(False, "failed"),
            Result(True, "ok"),
            Result(True, "ok"),
            Result(True, "ok"),
            Result(True, "ok"),
            Result(True, "ok"),
            Result(True, "ok"),
            Result(True, "ok"),
        ]
        result = KWinManager.apply_tiling_preset("vim")
        self.assertFalse(result.success)
        self.assertIn("Some bindings failed", result.message)


class TestReconfigureKWin(unittest.TestCase):
    """Tests for KWinManager.reconfigure_kwin()."""

    @patch('services.desktop.kwin.subprocess.run')
    def test_reconfigure_qdbus_success(self, mock_run):
        """Reconfigure succeeds via qdbus."""
        mock_run.return_value = MagicMock(returncode=0)
        result = KWinManager.reconfigure_kwin()
        self.assertTrue(result.success)
        self.assertIn("reconfigured", result.message.lower())

    @patch('services.desktop.kwin.subprocess.run')
    def test_reconfigure_dbus_send_fallback(self, mock_run):
        """Reconfigure falls back to dbus-send."""
        mock_run.side_effect = [
            MagicMock(returncode=1),  # qdbus fails
            MagicMock(returncode=0),  # dbus-send succeeds
        ]
        result = KWinManager.reconfigure_kwin()
        self.assertTrue(result.success)

    @patch('services.desktop.kwin.subprocess.run')
    def test_reconfigure_both_fail(self, mock_run):
        """Reconfigure handles both methods failing."""
        mock_run.return_value = MagicMock(returncode=1)
        result = KWinManager.reconfigure_kwin()
        self.assertFalse(result.success)

    @patch('services.desktop.kwin.subprocess.run')
    def test_reconfigure_exception(self, mock_run):
        """Reconfigure handles exception."""
        mock_run.side_effect = OSError("boom")
        result = KWinManager.reconfigure_kwin()
        self.assertFalse(result.success)


class TestAddWindowRule(unittest.TestCase):
    """Tests for KWinManager.add_window_rule()."""

    @patch('services.desktop.kwin.KWinManager.get_kreadconfig', return_value='kreadconfig6')
    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value='kwriteconfig6')
    @patch('services.desktop.kwin.subprocess.run')
    def test_add_window_rule_success(self, mock_run, mock_kwrite, mock_kread):
        """Add window rule succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stdout="0")
        result = KWinManager.add_window_rule("firefox", workspace=2, maximized=True)
        self.assertTrue(result.success)

    @patch('services.desktop.kwin.KWinManager.get_kreadconfig', return_value=None)
    @patch('services.desktop.kwin.KWinManager.get_kwriteconfig', return_value=None)
    def test_add_window_rule_no_tool(self, mock_kwrite, mock_kread):
        """Add window rule fails when tools not found."""
        result = KWinManager.add_window_rule("firefox")
        self.assertFalse(result.success)


if __name__ == '__main__':
    unittest.main()
