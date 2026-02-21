# Task Spec — v2.0.0 "Evolution"

## Tasks

### TASK-001: Version bump to 2.0.0

- **ID:** TASK-001
- **Files:** `version.py`, `pyproject.toml`, `.spec`, `.race-lock.json`
- **Dep:** none
- **Agent:** CodeGen
- **Description:** Bump version to 2.0.0 "Evolution" across all version files
- **Acceptance:** All 3 version files + race lock show 2.0.0
- **Docs:** CHANGELOG.md, ROADMAP.md
- **Tests:** Version tests pass with dynamic assertions
- **Status:** ✅ DONE

### TASK-002: Migrate services/software/

- **ID:** TASK-002
- **Files:** `services/software/flatpak.py`, `services/software/__init__.py`, `utils/flatpak_manager.py`
- **Dep:** TASK-001
- **Agent:** Builder
- **Description:** Move FlatpakManager from utils/ to services/software/. Convert utils/flatpak_manager.py to deprecation shim
- **Acceptance:** services/software/flatpak.py has full implementation, utils shim re-exports with warning
- **Docs:** none
- **Tests:** test_flatpak_manager.py updated to import from services.software
- **Status:** ✅ DONE

### TASK-003: Migrate services/desktop/

- **ID:** TASK-003
- **Files:** `services/desktop/*.py`, `utils/desktop_utils.py`, `utils/kwin_tiling.py`, `utils/tiling.py`, `utils/wayland_display.py`
- **Dep:** TASK-002
- **Agent:** Builder
- **Description:** Move 4 desktop modules to services/desktop/
- **Acceptance:** services/desktop/ has 4 service files + **init**.py, utils are deprecation shims
- **Docs:** none
- **Tests:** Related tests updated
- **Status:** ✅ DONE

### TASK-004: Migrate services/storage/

- **ID:** TASK-004
- **Files:** `services/storage/*.py`, `utils/cloud_sync.py`, `utils/state_teleport.py`
- **Dep:** TASK-002
- **Agent:** Builder
- **Description:** Move 2 storage modules to services/storage/
- **Acceptance:** services/storage/ populated, utils are shims
- **Docs:** none
- **Tests:** Related tests updated
- **Status:** ✅ DONE

### TASK-005: Migrate services/network/

- **ID:** TASK-005
- **Files:** `services/network/*.py`, `utils/network_utils.py`, `utils/network_monitor.py`, `utils/ports.py`, `utils/mesh_discovery.py`
- **Dep:** TASK-002
- **Agent:** Builder
- **Description:** Move 4 network modules to services/network/
- **Acceptance:** services/network/ populated, utils are shims
- **Docs:** none
- **Tests:** Related tests updated
- **Status:** ✅ DONE

### TASK-006: Migrate services/virtualization/

- **ID:** TASK-006
- **Files:** `services/virtualization/*.py`, `utils/virtualization.py`, `utils/vm_manager.py`, `utils/vfio.py`, `utils/disposable_vm.py`
- **Dep:** TASK-002
- **Agent:** Builder
- **Description:** Move 4 virtualization modules to services/virtualization/
- **Acceptance:** services/virtualization/ populated, utils are shims
- **Docs:** none
- **Tests:** Related tests updated
- **Status:** ✅ DONE

### TASK-007: Migrate services/security/

- **ID:** TASK-007
- **Files:** `services/security/*.py`, `utils/firewall_manager.py`, `utils/secureboot.py`, `utils/usbguard.py`, `utils/sandbox.py`, `utils/safety.py`, `utils/audit.py`, `utils/risk.py`
- **Dep:** TASK-002
- **Agent:** Builder
- **Description:** Move 7 security modules to services/security/. Move auth.py to api/
- **Acceptance:** services/security/ populated, utils are shims, auth.py in api/
- **Docs:** none
- **Tests:** Related tests updated
- **Status:** ✅ DONE

### TASK-008: Remove deprecated shims

- **ID:** TASK-008
- **Files:** `utils/process.py`, `utils/battery.py`, `utils/action_executor.py`
- **Dep:** TASK-003 through TASK-007
- **Agent:** CodeGen
- **Description:** Remove 3 legacy deprecated shim modules, fix remaining imports
- **Acceptance:** Shim files deleted, no imports reference them, tests updated
- **Docs:** none
- **Tests:** test_battery_shim.py deleted, test_clarity_update.py updated, 6 test files updated
- **Status:** ✅ DONE

### TASK-009: Populate core stubs

- **ID:** TASK-009
- **Files:** `core/agents/*.py`, `core/ai/*.py`, `core/diagnostics/*.py`, `core/export/*.py`
- **Dep:** TASK-007
- **Agent:** Builder
- **Description:** Populate 4 core stub directories with extracted logic from utils
- **Acceptance:** All 4 core dirs have real implementations, utils originals become shims
- **Docs:** none
- **Tests:** Existing tests still pass
- **Status:** ✅ DONE

### TASK-010: Update UI/CLI imports

- **ID:** TASK-010
- **Files:** 12 UI tab files, `cli/main.py`, `main_window.py`
- **Dep:** TASK-002 through TASK-009
- **Agent:** Sculptor
- **Description:** Update all UI tabs and CLI to import from new service locations
- **Acceptance:** No UI/CLI file imports from deprecated utils paths
- **Docs:** none
- **Tests:** All tests pass
- **Status:** ✅ DONE

### TASK-011: Update documentation

- **ID:** TASK-011
- **Files:** `ARCHITECTURE.md`, `CHANGELOG.md`, `ROADMAP.md`
- **Dep:** TASK-010
- **Agent:** CodeGen
- **Description:** Update architecture docs, changelog, and roadmap for v2.0.0
- **Acceptance:** All docs reflect v2.0.0 structure
- **Docs:** Self
- **Tests:** N/A
- **Status:** ✅ DONE

### TASK-012: Full verification

- **ID:** TASK-012
- **Files:** All
- **Dep:** TASK-011
- **Agent:** Guardian
- **Description:** Run full test suite, lint, typecheck, coverage gate
- **Acceptance:** 6016+ tests pass, ≥80% coverage, clean lint/typecheck
- **Docs:** none
- **Tests:** Full suite
- **Status:** ✅ DONE
