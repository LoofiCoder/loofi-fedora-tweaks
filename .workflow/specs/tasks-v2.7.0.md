# Tasks — v2.7.0 "API Migration Slice 3 (System Services)"

**Date**: 2026-02-25  
**Status**: In Progress  
**Arch Spec**: `arch-v2.7.0.md`

## Task List

---

### TASK001 — Prepare v2.7.0 planning contracts

**ID**: TASK001  
**Status**: Complete  
**Files**: `.workflow/specs/tasks-v2.7.0.md`, `.workflow/specs/arch-v2.7.0.md`, `ROADMAP.md`  
**Dep**: none  
**Agent**: project-coordinator  
**Description**: Establish canonical planning/design contracts for v2.7.0 as the next API migration slice.  
**Acceptance**: v2.7.0 tasks and architecture specs exist with dependency-ordered contracts and explicit scope boundaries.  
**Docs**: workflow specs + roadmap  
**Tests**: TASK005

---

### TASK002 — Service daemon handler foundation

**ID**: TASK002  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/daemon/handlers/service_handler.py`, `loofi-fedora-tweaks/daemon/handlers/__init__.py`  
**Dep**: TASK001  
**Agent**: backend-builder  
**Description**: Add daemon handler support for service/system operations with schema-consistent response envelopes and typed error mapping.  
**Acceptance**: handler returns strict envelope-compatible payloads for supported operations and explicit typed errors for unsupported/malformed requests.  
**Docs**: module docstrings (if behavior changes)  
**Tests**: TASK005

---

### TASK003 — System service API migration slice

**ID**: TASK003  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/services/system/service.py`, `loofi-fedora-tweaks/daemon/handlers/service_handler.py`  
**Dep**: TASK002  
**Agent**: backend-builder  
**Description**: Migrate system/service pathways to prefer daemon/API-backed execution while preserving existing method signatures and preferred-mode fallback behavior.  
**Acceptance**: callers remain backward-compatible, daemon-first behavior works for targeted operations, and preferred-mode fallback parity is preserved.  
**Docs**: module docstrings (if behavior changes)  
**Tests**: TASK005

---

### TASK004 — IPC compatibility hardening (service slice)

**ID**: TASK004  
**Status**: Complete  
**Files**: `loofi-fedora-tweaks/services/ipc/daemon_client.py`, `loofi-fedora-tweaks/services/ipc/types.py`  
**Dep**: TASK003  
**Agent**: backend-builder  
**Description**: Ensure daemon response parsing remains strict and backward-compatible for new service handler payload variants.  
**Acceptance**: malformed or incompatible payloads fail safely with typed errors while required/preferred mode behavior remains stable.  
**Docs**: module docstrings  
**Tests**: TASK005

---

### TASK005 — Test updates for slice-3 system migration

**ID**: TASK005  
**Status**: Complete  
**Files**: `tests/test_daemon_client.py`, `tests/test_ipc_fallback_modes.py`, `tests/test_system_service.py`  
**Dep**: TASK004  
**Agent**: test-writer  
**Description**: Add or update focused tests for daemon-backed system/service pathways, strict payload handling, and fallback behavior.  
**Acceptance**: targeted tests pass and validate success/failure/fallback semantics for touched code paths.  
**Docs**: module docstrings (if behavior changes)  
**Tests**: self

---

### TASK006 — Phase 3 prep: policy audit inventory + validator tightening plan

**ID**: TASK006  
**Status**: Complete  
**Files**: `.workflow/specs/arch-v2.7.0.md`, `.github/instructions/system_hardening_and_stabilization_guide.md`  
**Dep**: TASK005  
**Agent**: release-planner  
**Description**: Document bounded Phase 3 preparation items (policy inventory and validator hardening checklist) without expanding root capability scope.  
**Acceptance**: architecture spec and hardening guide references list concrete prep tasks with restrictive defaults and no privilege expansion.  
**Docs**: architecture/workflow docs  
**Tests**: TASK005

---

### TASK007 — Validation and progress metadata sync

**ID**: TASK007  
**Status**: Complete  
**Files**: `ROADMAP.md`, `.workflow/reports/run-manifest-v2.7.0.json`, `memory-bank/activeContext.md`, `memory-bank/progress.md`  
**Dep**: TASK006  
**Agent**: release-planner  
**Description**: Synchronize roadmap/workflow/memory state after v2.7.0 implementation and verification.  
**Acceptance**: canonical artifacts reflect the same version status and completion state with no contradictions.  
**Docs**: roadmap/workflow/memory-bank updates  
**Tests**: TASK005

