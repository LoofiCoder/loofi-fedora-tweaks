# Tasks — v2.8.0 "API Migration Slice 4 (Policy & Validator Hardening)"

**Date**: 2026-02-25  
**Status**: Complete  
**Arch Spec**: `arch-v2.8.0.md`

## Task List

---

### TASK001 — Prepare v2.8.0 planning contracts

**ID**: TASK001  
**Status**: Complete  
**Files**: `.workflow/specs/tasks-v2.8.0.md`, `.workflow/specs/arch-v2.8.0.md`, `ROADMAP.md`  
**Dep**: none  
**Agent**: project-coordinator  
**Description**: Establish canonical planning/design contracts for v2.8.0 as the active policy/validator hardening slice.  
**Acceptance**: v2.8.0 tasks and architecture specs exist with dependency-ordered contracts and restrictive scope boundaries.  
**Docs**: workflow specs + roadmap  
**Tests**: TASK005

---

### TASK002 — Build policy inventory map

**ID**: TASK002  
**Status**: Complete  
**Files**: `config/org.loofi.fedora-tweaks*.policy`, `.workflow/specs/arch-v2.8.0.md`, `loofi-fedora-tweaks/daemon/validators.py`  
**Dep**: TASK001  
**Agent**: backend-builder  
**Description**: Build a structured inventory mapping policy action IDs to capability scope and known caller pathways.  
**Acceptance**: policy inventory extraction is implemented and consumable for validator-gap analysis with no privilege expansion.  
**Docs**: architecture/workflow notes  
**Tests**: TASK005

---

### TASK003 — Validator coverage mapping + gap identification

**ID**: TASK003  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/daemon/handlers/`, `loofi-fedora-tweaks/services/ipc/`, `loofi-fedora-tweaks/daemon/validators.py`  
**Dep**: TASK002  
**Agent**: backend-builder  
**Description**: Map privileged daemon methods to existing validators and identify missing or weak schema checks.  
**Acceptance**: validator coverage map is generated and exposes prioritized unvalidated parameter gaps for existing privileged pathways.  
**Docs**: architecture/workflow notes  
**Tests**: TASK005

---

### TASK004 — Implement validator tightening for prioritized pathways

**ID**: TASK004  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/daemon/validators.py`, `loofi-fedora-tweaks/daemon/handlers/*.py`, `loofi-fedora-tweaks/services/ipc/types.py`  
**Dep**: TASK003  
**Agent**: backend-builder  
**Description**: Tighten parameter validation and fail-closed behavior for highest-risk privileged actions identified in TASK003.  
**Acceptance**: prioritized pathways enforce deny-by-default parameter validation with typed failure behavior.  
**Docs**: module docstrings (if behavior changes)  
**Tests**: TASK005

---

### TASK005 — Add focused validator hardening regression tests

**ID**: TASK005  
**Status**: Complete  
**Files**: `tests/test_*validator*.py`, `tests/test_daemon_client.py`, `tests/test_ipc_fallback_modes.py`, `tests/test_daemon_handlers_coverage.py`, `tests/test_ipc_types.py`  
**Dep**: TASK004  
**Agent**: test-writer  
**Description**: Add or update tests for malformed privileged payloads, deny-by-default behavior, and compatibility-safe error handling.  
**Acceptance**: focused tests pass and cover key success/failure edge cases for tightened validators; targeted hardening coverage reaches 91% across validator/handler/IPC guard modules.  
**Docs**: test notes in workflow artifacts  
**Tests**: self

---

### TASK006 — Validation and progress metadata sync

**ID**: TASK006  
**Status**: Complete  
**Files**: `ROADMAP.md`, `.workflow/reports/run-manifest-v2.8.0.json`, `memory-bank/activeContext.md`, `memory-bank/progress.md`  
**Dep**: TASK005  
**Agent**: release-planner  
**Description**: Synchronize roadmap/workflow/memory state after v2.8.0 implementation and verification.  
**Acceptance**: canonical artifacts reflect identical v2.8.0 status with no cross-file contradictions; `P6 PACKAGE` execution is completed via containerized Fedora build, and `P7 RELEASE` remains pending only for final git/tag push operations.  
**Docs**: roadmap/workflow/memory updates + package execution notes  
**Tests**: TASK005
