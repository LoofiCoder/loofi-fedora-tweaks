"""
Desktop environment utility helpers.

Provides colour-scheme detection via gsettings for GNOME/GTK desktops.
Migrated from utils/desktop_utils.py in v2.0.0 "Evolution".
"""

import subprocess


class DesktopUtils:
    """Static helpers for desktop environment detection."""

    @staticmethod
    def detect_color_scheme() -> str:
        """Detect the system colour-scheme preference via ``gsettings``.

        Queries ``org.gnome.desktop.interface color-scheme`` (GNOME / GTK).

        Returns
        -------
        str
            ``"dark"`` or ``"light"``.  Defaults to ``"dark"`` on failure.
        """
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            value = result.stdout.strip().strip("'\"")
            if "light" in value:
                return "light"
        except (OSError, subprocess.TimeoutExpired):
            pass
        return "dark"
