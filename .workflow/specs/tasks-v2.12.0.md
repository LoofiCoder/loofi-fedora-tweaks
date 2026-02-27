# Tasks — v2.12.0

- [x] ID: TASK-001 | Files: `ROADMAP.md, .workflow/specs/.race-lock.json, .workflow/specs/tasks-v2.12.0.md, .workflow/specs/arch-v2.12.0.md` | Dep: - | Agent: project-coordinator | Description: Activate v2.12.0 as the single active workflow target and scaffold canonical task/architecture contracts.
  Acceptance: `ROADMAP.md` contains exactly one ACTIVE version (v2.12.0), race-lock points to `v2.12.0` with `status=active`, and v2.12 task/arch spec files exist.
  Docs: none
  Tests: `tests/test_workflow_runner_locks.py`

- [x] ID: TASK-002 | Files: `loofi-fedora-tweaks/services/system/system.py, loofi-fedora-tweaks/services/package/service.py, loofi-fedora-tweaks/services/ipc/daemon_client.py` | Dep: TASK-001 | Agent: backend-builder | Description: Audit residual service methods and classify each as daemon-first or intentional-local-read with explicit inline contracts.
  Acceptance: Targeted methods document deterministic classification, maintain existing signatures, and preserve fallback compatibility semantics.
  Docs: none
  Tests: `tests/test_system_service.py, tests/test_package_service.py, tests/test_ipc_fallback_modes.py`

- [x] ID: TASK-003 | Files: `loofi-fedora-tweaks/services/system/system.py, loofi-fedora-tweaks/daemon/handlers/service_handler.py` | Dep: TASK-002 | Agent: backend-builder | Description: Implement bounded daemon-first migration for selected system-service residual methods identified in TASK-002.
  Acceptance: Migrated methods use daemon-first call flow with safe local fallback, no privilege expansion, no `shell=True`, and explicit subprocess timeout enforcement where local execution remains.
  Docs: none
  Tests: `tests/test_system_service.py, tests/test_daemon_client.py, tests/test_ipc_fallback_modes.py`

- [x] ID: TASK-004 | Files: `loofi-fedora-tweaks/services/package/service.py, loofi-fedora-tweaks/daemon/handlers/package_handler.py` | Dep: TASK-002 | Agent: backend-builder | Description: Normalize package-service residual paths for deterministic daemon/local parity and strict payload handling.
  Acceptance: Selected residual package paths have explicit daemon/local behavior, preserve return contracts, and maintain strict IPC payload compatibility.
  Docs: none
  Tests: `tests/test_package_service.py, tests/test_daemon_dbus.py, tests/test_ipc_fallback_modes.py`

- [x] ID: TASK-005 | Files: `tests/test_system_service.py, tests/test_daemon_client.py, tests/test_ipc_fallback_modes.py` | Dep: TASK-003 | Agent: test-writer | Description: Add focused regression tests for migrated system-service methods across daemon success, fallback, and local failure branches.
  Acceptance: New tests validate deterministic parity behavior with all system calls mocked via `@patch` and no root/network dependency.
  Docs: none
  Tests: `tests/test_system_service.py, tests/test_daemon_client.py, tests/test_ipc_fallback_modes.py`

- [x] ID: TASK-006 | Files: `tests/test_package_service.py, tests/test_daemon_dbus.py, tests/test_ipc_fallback_modes.py` | Dep: TASK-004 | Agent: test-writer | Description: Extend package-path regression coverage for residual parity and strict IPC envelope behavior.
  Acceptance: Tests cover daemon path, preferred-mode fallback, and malformed payload handling for updated package-service methods.
  Docs: none
  Tests: `tests/test_package_service.py, tests/test_daemon_dbus.py, tests/test_ipc_fallback_modes.py`

- [x] ID: TASK-007 | Files: `.workflow/reports/test-results-v2.12.0.json, .workflow/reports/run-manifest-v2.12.0.json` | Dep: TASK-005, TASK-006 | Agent: project-coordinator | Description: Generate canonical workflow report artifacts for v2.12.0 after test validation.
  Acceptance: Both report files exist with canonical `v2.12.0` naming and indicate non-zero executed tests for release gate compatibility.
  Docs: none
  Tests: `scripts/generate_workflow_reports.py, scripts/check_release_docs.py`

- [x] ID: TASK-008 | Files: `CHANGELOG.md, README.md, docs/releases/RELEASE-NOTES-v2.12.0.md, ROADMAP.md` | Dep: TASK-007 | Agent: release-planner | Description: Document v2.12.0 outcomes and close metadata after verification and packaging.
  Acceptance: Documentation reflects implemented behavior, roadmap status transitions to DONE at closure, and release notes summarize verified changes only.
  Docs: CHANGELOG, README, RELEASE-NOTES
  Tests: none
