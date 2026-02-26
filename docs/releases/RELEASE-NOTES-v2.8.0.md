# Release Notes -- v2.8.0 "API Migration Slice 4"

**Release Date:** 2026-02-26
**Codename:** API Migration Slice 4
**Theme:** Policy inventory execution and privileged validator hardening with fail-closed IPC safeguards.

## Summary

v2.8.0 completes the bounded hardening slice introduced after v2.7.0. The release
focuses on policy/validator correctness for privileged daemon pathways, enforces
stricter deny-by-default behavior for malformed payloads, and closes workflow
metadata drift across roadmap, lock, manifest, and memory-bank artifacts.

## Highlights

- Build policy inventory and validator coverage mapping for privileged daemon actions.
- Tighten parameter validation for prioritized privileged pathways with fail-closed handling.
- Expand focused hardening regression suites for validators, daemon handlers, and IPC payload types.
- Add regression checks for `check_fedora_review` local override and CI-guard behavior.
- Align runtime and packaging versions to `2.8.0` (`version.py`, `.spec`, `pyproject.toml`).
- Synchronize release-state artifacts (`ROADMAP.md`, `.race-lock.json`, `run-manifest-v2.8.0.json`, memory-bank docs).

## Changes

### Added

- Validator coverage and policy inventory helpers in `daemon/validators.py`.
- New gate-behavior tests in `tests/test_check_fedora_review.py` for local override and CI blocking.

### Changed

- Daemon validator pathways now enforce stricter deny-by-default parameter checks.
- Workflow and release-state docs now consistently represent v2.8.0 as completed/released.

### Fixed

- Documentation/version drift where current release references still pointed to v2.7.0.
- Stale artifact references in workflow/memory notes (`2.7.0` artifact names corrected to `2.8.0`).

## Stats

- **Targeted hardening suite:** 98 passed, 0 failed
- **Focused validation subset:** 174 passed, 14 skipped, 0 failed
- **Lint:** 0 errors
- **Typecheck:** pass (no blocking errors)

## Upgrade Notes

No intentional breaking UI or CLI contract changes.

