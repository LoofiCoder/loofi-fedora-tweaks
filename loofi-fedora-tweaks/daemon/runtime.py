"""Daemon runtime bootstrap."""

from __future__ import annotations

import logging

from daemon.interfaces import BUS_NAME
from daemon.server import DaemonService, dbus
from utils.daemon import Daemon as LegacyDaemon

logger = logging.getLogger(__name__)


def run_daemon() -> None:
    """Start D-Bus daemon service, fallback to legacy daemon loop if unavailable."""
    if dbus is None:
        logger.warning("dbus-python unavailable; falling back to legacy daemon mode")
        LegacyDaemon.run()
        return

    try:
        from dbus.mainloop.glib import DBusGMainLoop  # type: ignore[import-not-found]
        from gi.repository import GLib  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("GLib/dbus mainloop unavailable; falling back to legacy daemon mode")
        LegacyDaemon.run()
        return

    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    bus_name = dbus.service.BusName(BUS_NAME, bus=bus)
    DaemonService(bus_name)
    logger.info("Loofi daemon D-Bus service started on %s", BUS_NAME)
    GLib.MainLoop().run()
