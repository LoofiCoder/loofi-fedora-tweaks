# Release Notes — v2.12.0

## Overview

`v2.12.0 "API Migration Slice 8"` completes the bounded daemon-first migration for selected service-layer residual pathways and closes the corresponding workflow metadata slice.
This release remains stabilization-focused: no privilege-scope expansion, no new UI feature surface, and strict compatibility for daemon/local behavior.

## Highlights

- Migrated selected `SystemService` residual methods to daemon-first flow with safe local fallback parity.
- Normalized residual `PackageService` behavior for deterministic daemon/local compatibility.
- Expanded regression coverage for daemon success, preferred-mode fallback, and malformed payload handling.
- Generated canonical workflow artifacts for v2.12 with non-zero executed tests.
- Closed workflow metadata for the slice (`TASK-008`, roadmap status, race-lock status).

## Validation Summary

- Focused suite report (`.workflow/reports/test-results-v2.12.0.json`): `69 passed`, `57 skipped`, `0 failed`, `0 errors`.
- Workflow test report status: `pass`.
- Canonical run manifest present: `.workflow/reports/run-manifest-v2.12.0.json`.

## Upgrade Notes

- No breaking API changes intended for service consumers.
- Privilege model remains `pkexec`-only; no `sudo` and no `shell=True` introduced.
- Timeout enforcement and fallback-safe defaults remain mandatory on touched execution paths.

## Verified Commands

- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_system_service.py tests/test_daemon_client.py tests/test_ipc_fallback_modes.py tests/test_package_service.py tests/test_daemon_dbus.py tests/test_daemon_handlers_coverage.py --tb=no -p no:faulthandler -q`
- `python scripts/check_release_docs.py --require-logs`

---

For details, see [CHANGELOG.md](../../CHANGELOG.md) and [ROADMAP.md](../../ROADMAP.md).
