# Release Notes -- v2.7.0 "API Migration Slice 3"

**Release Date:** 2026-02-25
**Codename:** API Migration Slice 3
**Theme:** System-service daemon migration with strict IPC compatibility and cross-platform release hardening.

## Summary

v2.7.0 extends the API-first migration from package operations into system/service
operations. The release keeps caller-facing behavior stable by prioritizing
daemon-backed execution while preserving preferred-mode local fallback semantics.
It also hardens cross-platform compatibility and packaging reliability required
for predictable GitHub and COPR release automation.

## Highlights

- Add service daemon handler support and wire it into daemon handler exports.
- Migrate `SystemService` to daemon-first execution with strict fallback parity.
- Enforce strict system IPC payload validation in daemon client and shared IPC types.
- Validate daemon/system migration with focused regression suites.
- Improve Windows compatibility for POSIX-only API patch targets used by tests.
- Normalize release packaging version parsing to avoid CRLF-related artifact name drift.

## Changes

### Changed

- Route targeted system/service operations through daemon-first pathways with strict envelope handling.
- Strengthen daemon server method typing and dbus/no-dbus behavior consistency.
- Advance workflow release metadata to v2.7.0 for race lock and task contracts.

### Added

- `daemon/handlers/service_handler.py` for structured service operation handling.
- System payload validator coverage and daemon-client enforcement hooks.
- Release scaffold for `RELEASE-NOTES-v2.7.0.md` with synchronized version artifacts.

### Fixed

- Linux packaging script artifact-path mismatches caused by carriage returns in parsed version strings.
- Windows compatibility regressions for tests patching `os.sysconf`, `os.statvfs`, `os.getloadavg`, and `os.getuid`.

## Stats

- **Tests:** 7095 passed, 102 skipped, 0 failed (Linux validation run)
- **Lint:** 0 errors
- **Coverage:** Enforced by CI gate (`COVERAGE_THRESHOLD=77`)

## Upgrade Notes

No intentional breaking UI or CLI contract changes.
