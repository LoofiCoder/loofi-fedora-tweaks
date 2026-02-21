# Architecture Spec — v2.0.0 "Evolution"

## Summary

Service layer architecture migration. Moves 23 utils modules (~7,244 lines) into 6
service directories, removes 3 deprecated shims, and populates 4 empty core directories.
Zero new features — purely structural refactor.

## Design Principles

1. **Service layer pattern**: Follow `services/hardware/` and `services/system/` patterns
2. **Backward compatibility**: Migrated `utils/` modules become deprecation shims (re-exports)
3. **No new features**: Structural only — no new tabs, CLI commands, or API endpoints
4. **Incremental migration**: Low-complexity first (software), high-complexity last (security)

## Service Directory Migration Map

| Service Dir                | Source Utils Modules                                                                                    | Target Service Files                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `services/software/`       | `flatpak_manager.py`                                                                                    | `flatpak.py`                                             |
| `services/desktop/`        | `desktop_utils.py`, `kwin_tiling.py`, `tiling.py`, `wayland_display.py`                                 | `desktop.py`, `kwin.py`, `tiling.py`, `display.py`       |
| `services/storage/`        | `cloud_sync.py`, `state_teleport.py`                                                                    | `cloud_sync.py`, `teleport.py`                           |
| `services/network/`        | `network_utils.py`, `network_monitor.py`, `ports.py`, `mesh_discovery.py`                               | `network.py`, `monitor.py`, `ports.py`, `mesh.py`        |
| `services/virtualization/` | `virtualization.py`, `vm_manager.py`, `vfio.py`, `disposable_vm.py`                                     | `virtualization.py`, `vm.py`, `vfio.py`, `disposable.py` |
| `services/security/`       | `firewall_manager.py`, `secureboot.py`, `usbguard.py`, `sandbox.py`, `safety.py`, `audit.py`, `risk.py` | Same names in `services/security/`                       |

## Core Stubs Population

| Core Dir            | Source Utils                                                                              | Purpose                          |
| ------------------- | ----------------------------------------------------------------------------------------- | -------------------------------- |
| `core/agents/`      | `agents.py`, `agent_scheduler.py`, `agent_planner.py`, `agent_runner.py`, `arbitrator.py` | Agent orchestration ABCs + logic |
| `core/ai/`          | `ai.py`, `ai_models.py`, `context_rag.py`, `voice.py`                                     | AI feature abstractions          |
| `core/diagnostics/` | `health_score.py`, `health_timeline.py`, `health_detail.py`                               | Health/diagnostics engine        |
| `core/export/`      | `report_exporter.py`, `ansible_export.py`, `kickstart.py`                                 | Export format engines            |

## Deprecated Shims Removal

1. `utils/process.py` → removed (deprecated since v23.0)
2. `utils/battery.py` → removed (deprecated since v23.0)
3. `utils/action_executor.py` → removed (legacy re-export)
4. `core/executor/action_executor.py` legacy `run()` classmethod → removed

## UI Import Updates

| UI File                 | Old Import                  | New Import                |
| ----------------------- | --------------------------- | ------------------------- |
| `hardware_tab.py`       | `utils.battery`             | `services.hardware`       |
| `software_tab.py`       | `utils.flatpak_manager`     | `services.software`       |
| `desktop_tab.py`        | `utils.kwin_tiling` etc.    | `services.desktop`        |
| `network_tab.py`        | `utils.network_utils` etc.  | `services.network`        |
| `security_tab.py`       | `utils.usbguard` etc.       | `services.security`       |
| `virtualization_tab.py` | `utils.virtualization` etc. | `services.virtualization` |
| `community_tab.py`      | `utils.cloud_sync`          | `services.storage`        |
| `teleport_tab.py`       | `utils.state_teleport`      | `services.storage`        |
| `maintenance_tab.py`    | `utils.safety`              | `services.security`       |
| `diagnostics_tab.py`    | `utils.secureboot`          | `services.security`       |
| `mesh_tab.py`           | `utils.mesh_discovery`      | `services.network`        |
| `main_window.py`        | `utils.desktop_utils`       | `services.desktop`        |

## Special Cases

- `utils/auth.py` → `api/auth.py` (FastAPI-specific, not a service)
- `services/software/` absorbs only `flatpak_manager.py`; package management stays in `services/package/`

## Verification Criteria

- All 6016+ tests pass
- Coverage ≥ 80%
- Lint clean
- Typecheck clean
- Deprecation warnings fire on old utils imports
- All 4 entry modes work (GUI, CLI, daemon, API)
