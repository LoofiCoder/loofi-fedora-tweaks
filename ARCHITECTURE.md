# ARCHITECTURE.md — Loofi Fedora Tweaks

> **Canonical architecture reference.** All agent and instruction files MUST reference this document
> instead of duplicating architecture details. This file is updated when structure changes.
>
> **Version**: 4.0.0 "Atlas" | **Python**: 3.12+ | **Framework**: PyQt6 | **Platform**: Fedora Linux

## Project Structure

```text
loofi-fedora-tweaks/          # Application root (on PYTHONPATH)
├── main.py                   # Entry point — GUI (default), CLI (--cli), Daemon (--daemon)
├── version.py                # __version__, __version_codename__, __app_name__
├── core/                     # Business logic and system services [v4.0 Hub]
│   ├── diagnostics/          # Health & Repair Autopilot (HRA)
│   │   ├── health_registry.py# Central registry for system checks
│   │   ├── health_model.py   # Structured HealthCheck/HealthResult schemas
│   │   ├── upgrade_checker.py# Fedora version transition assistant
│   │   ├── task_dashboard.py # Goal-oriented task logic
│   │   └── gaming_audit.py   # Specialized hardware/gaming diagnostics
│   ├── executor/             # Action execution and safety
│   │   ├── action_model.py   # SystemAction with risk/rollback metadata
│   │   └── action_executor.py# Centralized safe command runner
│   ├── export/               # Diagnostic export services
│   │   ├── support_bundle_v2.py# Structured diagnostic bundle generator
│   │   └── ansible_exporter.py # ANSIBLE export logic
│   ├── plugins/              # Plugin discovery and loading logic
│   ├── agents/               # AgentRegistry, AgentPlanner, AgentExecutor
│   └── ai/                   # AI logic and prompt templates
├── ui/                       # PyQt6 widgets — Feature tabs + base class
│   ├── base_tab.py           # BaseTab ABC — shared CommandRunner wiring
│   ├── atlas_dashboard_tab.py# v4.0 Home - Task-based entry point
│   ├── task_wizard.py        # v4.0 Guided 4-step repair lifecycle
│   ├── support_bundle_wizard.py# v4.0 Export UI
│   ├── main_window.py        # MainWindow with sidebar + lazy-loaded tab stack
│   ├── icon_pack.py          # Semantic icon resolver + theme-aware tinting
│   ├── lazy_widget.py        # Lazy tab loader
│   ├── wizard.py             # First-run wizard
│   └── ...                   # Feature tabs (maintenance, software, etc.)
├── utils/                    # Shared utilities
│   ├── commands.py           # PrivilegedCommand builder (pkexec)
│   ├── command_runner.py     # CommandRunner (QProcess async wrapper)
│   ├── system.py             # SystemManager (Atomic detection, etc.)
│   ├── experience_level.py   # Beginner/Intermediate/Advanced modes
│   └── ...
├── services/                 # Legacy/Niche domain services
├── cli/                      # CLI subcommands
├── config/                   # Apps and polkit policies
└── web/                      # Web dashboard logic
```

## Three Entry Modes


| Mode       | Flag       | Module                   | Purpose                                    |
| ---------- | ---------- | ------------------------ | ------------------------------------------ |
| **GUI**    | (default)  | `main.py` → `MainWindow` | PyQt6 desktop app with 28 lazy-loaded tabs |
| **CLI**    | `--cli`    | `cli/main.py`            | Subcommands with `--json` output           |
| **Daemon** | `--daemon` | `daemon/runtime.py`      | D-Bus daemon host + legacy fallback        |

## Layer Rules (STRICT)

| Layer        | Path          | Allowed                                             | Forbidden                     |
| ------------ | ------------- | --------------------------------------------------- | ----------------------------- |
| **UI**       | `ui/*_tab.py` | PyQt6 widgets, signals, BaseTab                     | `subprocess`, business logic  |
| **Services** | `services/*/` | Domain services (security, network, storage, etc.)  | `import PyQt6`, UI references |
| **Core**     | `core/*/`     | Domain modules (agents, ai, diagnostics, export)    | `import PyQt6`, UI references |
| **Utils**    | `utils/*.py`  | Shared ops, commands, errors; backward-compat shims | `import PyQt6`, UI references |
| **CLI**      | `cli/main.py` | Argument parsing, calls services/core/utils         | `import ui`, PyQt6            |

**Key rule**: `services/` and `core/` hold domain logic. `utils/` retains shared infrastructure (`commands.py`, `errors.py`, `operations.py`) and backward-compatible shims. GUI and CLI are consumers only.

## Tab Layout (28 Feature Tabs)

### Sidebar Categories

| Order | Category    | Icon                   |
| ----- | ----------- | ---------------------- |
| 1     | System      | `overview-dashboard`   |
| 2     | Packages    | `packages-software`    |
| 3     | Hardware    | `hardware-performance` |
| 4     | Network     | `network-connectivity` |
| 5     | Security    | `security-shield`      |
| 6     | Appearance  | `appearance-theme`     |
| 7     | Tools       | `developer-tools`      |
| 8     | Maintenance | `maintenance-health`   |

| #   | Tab                | File                     | Consolidates                             |
| --- | ------------------ | ------------------------ | ---------------------------------------- |
| 1   | Home               | `dashboard_tab.py`       | Dashboard                                |
| 2   | System Info        | `system_info_tab.py`     | System details                           |
| 3   | System Monitor     | `monitor_tab.py`         | Performance + Processes                  |
| 4   | Maintenance        | `maintenance_tab.py`     | Updates + Cleanup + Overlays             |
| 5   | Hardware           | `hardware_tab.py`        | Hardware + HP Tweaks + Bluetooth         |
| 6   | Software           | `software_tab.py`        | Apps + Repos                             |
| 7   | Security & Privacy | `security_tab.py`        | Security + Privacy                       |
| 8   | Network            | `network_tab.py`         | Connections + DNS + Privacy + Monitoring |
| 9   | Gaming             | `gaming_tab.py`          | Gaming setup                             |
| 10  | Desktop            | `desktop_tab.py`         | Director + Theming                       |
| 11  | Development        | `development_tab.py`     | Containers + Developer tools             |
| 12  | AI Lab             | `ai_enhanced_tab.py`     | AI features                              |
| 13  | Automation         | `automation_tab.py`      | Scheduler + Replicator + Pulse           |
| 14  | Community          | `community_tab.py`       | Presets + Marketplace                    |
| 15  | Diagnostics        | `diagnostics_tab.py`     | Watchtower + Boot                        |
| 16  | Virtualization     | `virtualization_tab.py`  | VMs + VFIO + Disposable                  |
| 17  | Loofi Link         | `mesh_tab.py`            | Mesh + Clipboard + File Drop             |
| 18  | State Teleport     | `teleport_tab.py`        | Workspace Capture/Restore                |
| 19  | Performance        | `performance_tab.py`     | Auto-Tuner                               |
| 20  | Snapshots          | `snapshot_tab.py`        | Snapshot Timeline                        |
| 21  | Logs               | `logs_tab.py`            | Smart Log Viewer                         |
| 22  | Storage            | `storage_tab.py`         | Disks + Mounts + SMART                   |
| 23  | Health Timeline    | `health_timeline_tab.py` | System health over time                  |
| 24  | Profiles           | `profiles_tab.py`        | User profiles management                 |
| 25  | Extensions         | `extensions_tab.py`      | GNOME/KDE extensions browser             |
| 26  | Backup             | `backup_tab.py`          | Backup wizard + Timeshift/Snapper        |
| 27  | Agents             | `agents_tab.py`          | AI agent management                      |
| 28  | Settings           | `settings_tab.py`        | App settings                             |

Consolidated tabs use `QTabWidget` for sub-navigation within the tab.

### Sidebar Index (v48.0)

The sidebar uses a `SidebarIndex` (`dict[str, SidebarEntry]`) keyed by `PluginMetadata.id` for O(1) tab lookups. `SidebarEntry` holds the tree item, page widget, metadata, and status.

Key methods:

- `_find_or_create_category(category)` — cached category item lookup
- `_create_tab_item(...)` — creates tree item with badge and icon
- `_register_in_index(plugin_id, entry)` — populates index and content area
- `add_page(...)` — public API orchestrator (backward-compatible)
- `switch_to_tab(name)` — O(1) by plugin ID, fallback by display name
- `_set_tab_status(tab_id, status)` — O(1) status update via data role

Status rendering uses `SidebarItemDelegate` with colored dots instead of text markers.

## Critical Patterns

### 1. PrivilegedCommand (ALWAYS unpack)

```python
from utils.commands import PrivilegedCommand

binary, args, desc = PrivilegedCommand.dnf("install", "package")
cmd = [binary] + args  # ["pkexec", "dnf", "install", "-y", "package"]
# ⚠️ Never pass the raw tuple to subprocess.run()
```

- Returns `Tuple[str, List[str], str]` — binary, args, description
- Auto-detects Atomic (rpm-ostree) vs Traditional (dnf)
- `dnf()` adds `-y` internally — don't duplicate

### 2. BaseTab for UI Tabs

```python
from ui.base_tab import BaseTab

class MyTab(BaseTab):
    def __init__(self):
        super().__init__()
        # Provides: self.output_area, self.runner (CommandRunner),
        # self.run_command(), self.append_output(), self.add_section()
```

### 3. CommandRunner (Async GUI)

```python
from utils.command_runner import CommandRunner
self.runner = CommandRunner()
self.runner.finished.connect(self.on_done)
self.runner.run_command("pkexec", ["dnf", "update", "-y"])
```

Never block the GUI thread with synchronous subprocess calls.

### 4. Operations Tuple Pattern

```python
@staticmethod
def clean_cache() -> Tuple[str, List[str], str]:
    pm = SystemManager.get_package_manager()
    if pm == "rpm-ostree":
        return ("pkexec", ["rpm-ostree", "cleanup", "--base"], "Cleaning...")
    return ("pkexec", ["dnf", "clean", "all"], "Cleaning...")
```

### 5. Error Framework

```python
from utils.errors import LoofiError, DnfLockedError, CommandFailedError
raise DnfLockedError(hint="Package manager is busy.")
# Each error has: code, hint, recoverable attributes
```

### 6. Confirm Dialog (Dangerous Ops)

```python
from ui.confirm_dialog import ConfirmActionDialog
if ConfirmActionDialog.confirm(self, "Delete snapshots", "Cannot be undone"):
    # proceed
```

### 7. Atomic Fedora

```python
pm = SystemManager.get_package_manager()  # "dnf" or "rpm-ostree"
if SystemManager.is_atomic():
    # rpm-ostree path
```

Always use `SystemManager.get_package_manager()` — **never hardcode `dnf`**.

### 8. Privilege Escalation

**Only `pkexec`** — never `sudo`. Policy: `config/org.loofi.fedora-tweaks.policy`.

### 9. Lazy Tab Loading

```python
from core.plugins.loader import PluginLoader
from core.plugins.registry import PluginRegistry
from ui.lazy_widget import LazyWidget

loader = PluginLoader(detector=detector)
loader.load_builtins(context=context)
for plugin in PluginRegistry.instance():
    meta = plugin.metadata()
    lazy_widget = LazyWidget(plugin.create_widget)
    self.add_page(name=meta.name, icon=meta.icon, widget=lazy_widget, category=meta.category)
```

### 10. Safety & History

- `SafetyManager.confirm_action()` — snapshot prompt before risky ops
- `HistoryManager.log_change()` — action log with undo commands (max 50)

### 11. Icon System (Semantic IDs + Theme Tint)

- Sidebar, dashboard, and quick actions use semantic icon IDs (for example `home`, `update`, `security-shield`) instead of emoji glyphs.
- Runtime loading and tinting are centralized in `ui/icon_pack.py`.
- Icon roots are checked in this order:
  - `assets/icons/`
  - `loofi-fedora-tweaks/assets/icons/`
- `icon-map.json` maps semantic IDs to assets; SVG is preferred with PNG fallback (`16`, `20`, `24`, `32`).
- Main sidebar applies selection-aware tint variants so active rows are brighter and inactive rows stay integrated with the theme.

## Testing Rules

- **Framework**: `unittest` + `unittest.mock`
- **Decorators only**: `@patch`, never context managers
- **Mock everything**: `subprocess.run`, `check_output`, `shutil.which`, `os.path.exists`, `builtins.open`
- **Both paths**: Test success AND failure
- **No root**: Tests run in CI without privileges
- **Path setup**: `sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'loofi-fedora-tweaks'))`
- **Coverage**: 80%+ current, 85% stretch goal

## Adding a Feature

1. **Logic**: `utils/new_feature.py` — `@staticmethod`, return ops tuples
2. **UI**: `ui/new_feature_tab.py` — inherit `BaseTab`
3. **CLI**: Subcommand in `cli/main.py` with `--json`
4. **Test**: `tests/test_new_feature.py` — mock all system calls
5. **Register**: plugin metadata + registry category with semantic `icon="..."` token (no emoji)
6. **Docs**: `CHANGELOG.md`, `README.md`

## Version Management

Three files MUST stay in sync (use `scripts/bump_version.py` for cascade):

- `loofi-fedora-tweaks/version.py` — `__version__`, `__version_codename__`
- `loofi-fedora-tweaks.spec` — `Version:`
- `pyproject.toml` — `version`

## Build & Run

```bash
./run.sh                                                    # Dev run
PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/ -v   # Tests
bash scripts/build_rpm.sh                                   # Build RPM
flake8 loofi-fedora-tweaks/ --max-line-length=150 --ignore=E501,W503,E402,E722,E203
```

## Config & Conventions

- **Config dir**: `~/.config/loofi-fedora-tweaks/`
- **App catalog**: `config/apps.json`
- **QSS**: `assets/modern.qss` — use `setObjectName()` for targeting
- **Icon pack**: `assets/icons/` + `loofi-fedora-tweaks/assets/icons/` (`svg/`, `png/`, `icon-map.json`)
- **i18n**: `self.tr("...")` for all user-visible strings
- **Naming**: `ui/*_tab.py` → `*Tab`; `utils/*.py` → `*Manager`/`*Ops` with `@staticmethod`
- **Plugins**: Extend `LoofiPlugin` ABC, place in `plugins/<name>/plugin.py`
├── daemon/                   # D-Bus daemon host + validators + handlers (v2.4.0)
│   ├── runtime.py            # Daemon bootstrap and GLib main loop
│   ├── server.py             # D-Bus object methods (org.loofi.FedoraTweaks.Daemon1)
│   ├── contracts.py          # Standard JSON response envelope
│   ├── validators.py         # Input validation for privileged operations
│   └── handlers/             # Network/firewall/port-audit execution handlers
