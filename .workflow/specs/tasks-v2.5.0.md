# Tasks — v2.5.0 "API Migration Slice 1"

**Date**: 2026-02-25  
**Status**: Complete  
**Arch Spec**: `arch-v2.5.0.md`

## Task List

---

### TASK001 — Activate v2.5.0 workflow cycle

**ID**: TASK001  
**Status**: Complete  
**Files**: `.workflow/specs/.race-lock.json`, `.workflow/specs/tasks-v2.5.0.md`, `.workflow/specs/arch-v2.5.0.md`, `.workflow/reports/run-manifest-v2.5.0.json`  
**Dep**: none  
**Agent**: project-coordinator  
**Description**: Activate the v2.5.0 workflow cycle and define canonical task/architecture contracts for Phase 2 slice-1 work.  
**Acceptance**: v2.5.0 lock and spec artifacts exist and describe network/firewall API migration scope.  
**Docs**: workflow specs  
**Tests**: TASK005

---

### TASK002 — Network service API migration slice

**ID**: TASK002  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/services/network/network.py`, `loofi-fedora-tweaks/daemon/handlers/network_handler.py`  
**Dep**: TASK001  
**Agent**: backend-builder  
**Description**: Reduce parsing-heavy network command execution by preferring API-backed daemon/service pathways while preserving current method signatures and fallback semantics.  
**Acceptance**: network service behavior remains compatible for callers, with improved structured data handling and no regressions in preferred mode fallback behavior.  
**Docs**: docstrings (if behavior changes)  
**Tests**: TASK005

---

### TASK003 — Firewall service API migration slice

**ID**: TASK003  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/services/security/firewall.py`, `loofi-fedora-tweaks/daemon/handlers/firewall_handler.py`  
**Dep**: TASK002  
**Agent**: backend-builder  
**Description**: Reduce parsing-heavy firewall command execution by preferring API-backed daemon/service pathways while preserving current method signatures and fallback semantics.  
**Acceptance**: firewall service behavior remains compatible for callers, with improved structured data handling and no regressions in preferred mode fallback behavior.  
**Docs**: docstrings (if behavior changes)  
**Tests**: TASK005

---

### TASK004 — IPC behavior and compatibility hardening

**ID**: TASK004  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/services/ipc/daemon_client.py`, `loofi-fedora-tweaks/services/ipc/types.py`  
**Dep**: TASK003  
**Agent**: backend-builder  
**Description**: Ensure daemon response handling remains strict and backward-compatible for network/firewall migration cases.  
**Acceptance**: malformed or unsupported daemon payloads fail safely with explicit typed errors; preferred mode fallback remains intact.  
**Docs**: docstrings  
**Tests**: TASK005

---

### TASK005 — Test updates for slice-1 migration

**ID**: TASK005  
**Status**: Complete  
**Files**: `tests/test_daemon_dbus.py`, `tests/test_daemon_client.py`, `tests/test_ipc_fallback_modes.py`  
**Dep**: TASK004  
**Agent**: test-writer  
**Description**: Add or update focused tests for network/firewall daemon pathways and fallback behavior.  
**Acceptance**: updated test targets pass and verify both success and failure/fallback modes for touched paths.  
**Docs**: module docstrings  
**Tests**: self

---

### TASK006 — Validation and progress sync

**ID**: TASK006  
**Status**: Complete  
**Files**: `ROADMAP.md`, `.workflow/reports/run-manifest-v2.5.0.json`  
**Dep**: TASK005  
**Agent**: release-planner  
**Description**: Sync roadmap/workflow progress metadata after slice-1 implementation and verification.  
**Acceptance**: workflow artifacts and roadmap status reflect executed v2.5.0 slice state.  
**Docs**: ROADMAP/workflow report updates  
**Tests**: TASK005
