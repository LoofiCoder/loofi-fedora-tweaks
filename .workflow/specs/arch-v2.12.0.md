# Architecture Spec - v2.12.0 "Service Parity Completion"

## Design Rationale

v2.12.0 completes the next bounded daemon/API migration step by targeting service-layer
residuals that still rely on local execution defaults. The slice remains stabilization-only:
no root-capability expansion, no UI feature expansion, and no IPC envelope contract breaks.

## Reviewed Inputs

- `.workflow/specs/tasks-v2.12.0.md`
- `AGENTS.md` (critical rules and patterns)
- `ARCHITECTURE.md` (layer boundaries and executor/IPC constraints)
- `ROADMAP.md` (active version scope)

## Scope

- TASK-001: activate v2.12.0 metadata + canonical workflow artifacts.
- TASK-002: classify residual service methods as daemon-first or intentional-local-read.
- TASK-003: bounded system-service residual migration.
- TASK-004: bounded package-service residual parity normalization.
- TASK-005/TASK-006: focused regressions for parity and fallback guarantees.
- TASK-007: generate canonical workflow reports for release gates.
- TASK-008: release documentation and closure metadata alignment.

## Non-Goals

1. No new privileged capabilities or policy surface expansion.
2. No new UI tabs or CLI features unrelated to residual parity.
3. No broad refactors outside selected residual methods.
4. No `shell=True`, no `sudo`, no timeout-less subprocess calls.

## Dependency Graph and Sequencing (Acyclic)

```text
TASK-001 -> TASK-002 -> {TASK-003, TASK-004}
TASK-003 -> TASK-005
TASK-004 -> TASK-006
TASK-005 + TASK-006 -> TASK-007 -> TASK-008
```

## Design Decisions

### D1 - Residual Method Classification Before Migration

- **Layer**: `services/` + daemon handlers
- **Files**: `services/system/system.py`, `services/package/package.py`, `services/ipc/client.py`
- **Decision**: classify each candidate method explicitly before code migration.
- **Why**: avoids accidental privilege expansion and keeps daemon/local behavior deterministic.

### D2 - Bounded System-Service Migration

- **Layer**: `services/system/` + `daemon/handlers/`
- **Files**: `services/system/system.py`, `daemon/handlers/service_handler.py`
- **Decision**: migrate only the residual methods selected in TASK-002 using daemon-first with preferred-mode fallback.
- **Constraints**: preserve method signatures/return types; keep explicit timeout where local subprocess paths remain.

### D3 - Package-Service Parity Normalization

- **Layer**: `services/package/` + `daemon/handlers/`
- **Files**: `services/package/package.py`, `daemon/handlers/package_handler.py`
- **Decision**: close residual parity drift without changing IPC response contracts.
- **Constraints**: enforce strict payload compatibility and deterministic fallback behavior.

### D4 - Regression-First Safety Gate

- **Layer**: `tests/`
- **Files**: `tests/test_system_service.py`, `tests/test_package_service.py`, `tests/test_daemon_client.py`, `tests/test_daemon_dbus.py`, `tests/test_ipc_fallback_modes.py`
- **Decision**: add focused regressions for each migrated path before release reporting.
- **Constraints**: `@patch` decorators only, no root/network dependency, mock subprocess and file/system calls.

### D5 - Canonical Workflow Artifacts

- **Layer**: `.workflow/reports/`
- **Files**: `test-results-v2.12.0.json`, `run-manifest-v2.12.0.json`
- **Decision**: enforce canonical `vX.Y.Z` naming and non-zero test execution reports for release gate compatibility.

## Risk Review and Mitigation

- **Risk R1**: behavior drift in fallback mode.
  - **Mitigation**: preserve existing signatures and add fallback regression tests.
- **Risk R2**: privilege-scope creep from residual migration.
  - **Mitigation**: method-level classification first, explicit non-goals, no new root paths.
- **Risk R3**: release gate false-green from incomplete reports.
  - **Mitigation**: generate canonical workflow reports and validate with release-doc gate.

## Verification Commands (Slice Exit)

- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_system_service.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_package_service.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_daemon_client.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_daemon_dbus.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_ipc_fallback_modes.py -v`
- `python scripts/generate_workflow_reports.py`
- `python scripts/check_release_docs.py --require-logs`

## Blocking Concerns

None identified for kickoff. Implementation can proceed starting at TASK-002.
