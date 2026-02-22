"""Regression tests for ui/software_tab.py feedback helpers."""
# pyright: reportAttributeAccessIssue=false

import importlib
import os
import sys
import types
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "loofi-fedora-tweaks"))


_original_modules = {}


def _install_stubs():
    class _Dummy:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            if name == "tr":
                return lambda text, *a, **kw: text
            return MagicMock()

    class _Signal:
        def __init__(self):
            self.connect = MagicMock()

    qt_widgets = types.ModuleType("PyQt6.QtWidgets")
    qt_widgets.QWidget = _Dummy
    qt_widgets.QVBoxLayout = _Dummy
    qt_widgets.QHBoxLayout = _Dummy
    qt_widgets.QLabel = _Dummy
    qt_widgets.QPushButton = _Dummy
    qt_widgets.QTextEdit = _Dummy
    qt_widgets.QGroupBox = _Dummy
    qt_widgets.QTabWidget = _Dummy
    qt_widgets.QFrame = _Dummy
    qt_widgets.QCheckBox = _Dummy
    qt_widgets.QLineEdit = _Dummy
    qt_widgets.QScrollArea = _Dummy
    qt_widgets.QListWidget = _Dummy

    qt_core = types.ModuleType("PyQt6.QtCore")
    qt_core.Qt = types.SimpleNamespace()

    pyqt = types.ModuleType("PyQt6")
    pyqt.QtWidgets = qt_widgets
    pyqt.QtCore = qt_core

    base_tab_mod = types.ModuleType("ui.base_tab")

    class _StubBaseTab(_Dummy):
        def show_success(self, message: str):
            return None

        def show_error(self, message: str):
            return None

    base_tab_mod.BaseTab = _StubBaseTab

    tab_utils_mod = types.ModuleType("ui.tab_utils")
    tab_utils_mod.configure_top_tabs = lambda *a, **kw: None

    cmd_runner_mod = types.ModuleType("utils.command_runner")

    class _StubCommandRunner:
        def __init__(self, *args, **kwargs):
            self.output_received = _Signal()
            self.finished = _Signal()
            self.progress_update = _Signal()
            self.error_occurred = _Signal()
            self.run_command = MagicMock()

    cmd_runner_mod.CommandRunner = _StubCommandRunner

    metadata_mod = types.ModuleType("core.plugins.metadata")

    class _StubPluginMetadata:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    metadata_mod.PluginMetadata = _StubPluginMetadata

    batch_ops_mod = types.ModuleType("utils.batch_ops")
    batch_ops_mod.BatchOpsManager = type(
        "BatchOpsManager",
        (),
        {
            "batch_install": staticmethod(lambda packages: ("pkexec", ["dnf", "install", "-y"] + packages, "install")),
            "batch_remove": staticmethod(lambda packages: ("pkexec", ["dnf", "remove", "-y"] + packages, "remove")),
        },
    )

    software_utils_mod = types.ModuleType("utils.software_utils")
    software_utils_mod.SoftwareUtils = type(
        "SoftwareUtils",
        (),
        {
            "is_check_command_satisfied": staticmethod(lambda cmd: False),
            "get_fedora_version": staticmethod(lambda: "43"),
        },
    )

    commands_mod = types.ModuleType("utils.commands")
    commands_mod.PrivilegedCommand = type(
        "PrivilegedCommand",
        (),
        {
            "dnf": staticmethod(lambda *args, **kwargs: ("pkexec", ["dnf"] + list(args), "dnf")),
        },
    )

    remote_config_mod = types.ModuleType("utils.remote_config")

    class _StubFetcher:
        def __init__(self):
            self.config_ready = _Signal()
            self.config_error = _Signal()

        def start(self):
            return None

    remote_config_mod.AppConfigFetcher = _StubFetcher

    tooltips_mod = types.ModuleType("ui.tooltips")
    tooltips_mod.SW_BATCH_INSTALL = ""
    tooltips_mod.SW_BATCH_REMOVE = ""
    tooltips_mod.SW_CODECS = ""
    tooltips_mod.SW_FLATHUB = ""
    tooltips_mod.SW_RPM_FUSION = ""
    tooltips_mod.SW_SEARCH = ""

    module_map = {
        "PyQt6": pyqt,
        "PyQt6.QtWidgets": qt_widgets,
        "PyQt6.QtCore": qt_core,
        "ui.base_tab": base_tab_mod,
        "ui.tab_utils": tab_utils_mod,
        "utils.command_runner": cmd_runner_mod,
        "core.plugins.metadata": metadata_mod,
        "utils.batch_ops": batch_ops_mod,
        "utils.software_utils": software_utils_mod,
        "utils.commands": commands_mod,
        "utils.remote_config": remote_config_mod,
        "ui.tooltips": tooltips_mod,
    }

    for name, mod in module_map.items():
        _original_modules[name] = sys.modules.get(name)
        sys.modules[name] = mod


def _uninstall_stubs():
    for name, mod in _original_modules.items():
        if mod is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = mod


_install_stubs()
sys.modules.pop("ui.software_tab", None)
_st = importlib.import_module("ui.software_tab")

for _name, _orig in _original_modules.items():
    if _name == "ui.software_tab":
        continue
    if _orig is None:
        sys.modules.pop(_name, None)
    else:
        sys.modules[_name] = _orig


class TestApplicationsSubTabFeedback(unittest.TestCase):
    def setUp(self):
        self.tab = _st._ApplicationsSubTab()
        self.tab.output_area = MagicMock()
        self.tab.append_output = MagicMock()
        self.tab.refresh_list = MagicMock()

    def test_command_finished_success_calls_show_success(self):
        self.tab.show_success = MagicMock()
        self.tab.command_finished(0)
        self.tab.show_success.assert_called_once()
        self.tab.refresh_list.assert_called_once()

    def test_command_finished_failure_calls_show_error(self):
        self.tab.show_error = MagicMock()
        self.tab.command_finished(1)
        self.tab.show_error.assert_called_once()
        self.tab.refresh_list.assert_not_called()


class TestRepositoriesSubTabFeedback(unittest.TestCase):
    def setUp(self):
        self.tab = _st._RepositoriesSubTab()
        self.tab.output_area = MagicMock()
        self.tab.append_output = MagicMock()

    def test_command_finished_success_calls_show_success(self):
        self.tab.show_success = MagicMock()
        self.tab.command_finished(0)
        self.tab.show_success.assert_called_once()

    def test_command_finished_failure_calls_show_error(self):
        self.tab.show_error = MagicMock()
        self.tab.command_finished(2)
        self.tab.show_error.assert_called_once()


class TestSoftwareTabSourceLevel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "loofi-fedora-tweaks",
            "ui",
            "software_tab.py",
        )
        with open(path, "r", encoding="utf-8") as fh:
            cls.source = fh.read()

    def test_applications_subtab_inherits_base_tab(self):
        self.assertIn("class _ApplicationsSubTab(BaseTab)", self.source)

    def test_repositories_subtab_inherits_base_tab(self):
        self.assertIn("class _RepositoriesSubTab(BaseTab)", self.source)


def tearDownModule():
    sys.modules.pop("ui.software_tab", None)
    _uninstall_stubs()


if __name__ == "__main__":
    unittest.main()
