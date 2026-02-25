# Progress — Loofi Fedora Tweaks

## What Works

### Application

- 28 feature tabs across 8 categories (System, Packages, Hardware, Network, Security, Appearance, Tools, Maintenance)
- 4 entry modes: GUI, CLI (`--cli`), Daemon (`--daemon`), API (`--api`)
- Lazy tab loading for fast startup
- Plugin marketplace with sandboxing, ratings, reviews, hot-reload
- Experience levels (Beginner/Intermediate/Expert)
- Guided tour and onboarding wizard
- Health score dashboard with timeline and diagnostics
- Abyss (dark) and Light themes
- Command palette for quick actions
- Dangerous operation confirmation dialogs with safety snapshots
- Ansible export, kickstart generation, report export
- AI agent runtime with planning and scheduling

### Infrastructure

- 228+ test files, 6383+ tests, 81%+ coverage (80% CI-enforced)
- RPM packaging via COPR (`loofitheboss/loofi-fedora-tweaks`)
- Flatpak and AppImage distribution
- Systemd service for daemon mode
- Polkit policy for privilege escalation
- CI pipeline with coverage gate, stabilization rules, docs gate, bandit security scanner
- Structured service layer (9 domains) + core layer (8 domains)
- All 6 stabilization/hardening phases complete

### Version History Summary

- Legacy (integer): v21–v50 — UX, architecture, plugins, stabilization, hardening
- SemVer: v1.0.0 — version renormalization
- SemVer: v2.0.0 "Evolution" — service layer migration
- SemVer: v2.1.0 "Continuity" — workflow realignment and adapter sync
- SemVer: v2.2.0 "Velocity" — performance caching and subprocess safety
- SemVer: v2.2.1 (patch) — CI @patch target corrections
- SemVer: v2.2.2 (patch) — CI coverage threshold and tasks spec gate
- SemVer: v2.3.0 "Insight" — diagnostics expansion
- SemVer: v2.4.0 "Evolution" — daemon foundation + IPC fallback alignment
- SemVer: v2.5.0 "API Slice 1" — network/firewall API migration
- SemVer: v2.6.0 "API Slice 2" — package API migration (active)
- SemVer: v2.7.0 "API Slice 3" — system-service API migration + Phase 3 prep (in progress)

Current active semantic cycle: v2.6.0.

## What's Left to Build

### Active (v2.6.0 — in progress)

- [x] TASK001 Activate v2.6.0 workflow cycle
- [x] TASK002 Package daemon handler foundation
- [x] TASK003 Package service API migration slice
- [x] TASK004 IPC behavior and compatibility hardening (packages)
- [x] TASK005 Test updates for slice-2 package migration
- [x] TASK006 Planning artifact cleanup sync
- [x] TASK007 Validation and progress sync

### Next Slice (v2.7.0 — in progress)

- [x] TASK001 Prepare v2.7.0 planning contracts
- [x] TASK002 Service daemon handler foundation
- [x] TASK003 System service API migration slice
- [x] TASK004 IPC compatibility hardening (service slice)
- [x] TASK005 Test updates for slice-3 system migration
- [x] TASK006 Phase 3 prep: policy audit inventory + validator tightening plan
- [x] TASK007 Validation and progress metadata sync

## Current Status

**v2.6.0 "API Migration Slice 2 (Packages)"**: 🚧 IN PROGRESS — implementation/documentation complete; package + release phases pending.
**v2.7.0 "API Migration Slice 3 (System Services)"**: 🚧 IN PROGRESS — implementation and focused verification completed; workflow activation pending phase progression.
**v2.5.0 "API Migration Slice 1"**: ✅ COMPLETE — network/firewall daemon-first migration.
**v2.4.0 "Evolution"**: ✅ COMPLETE — daemon foundation and hardening alignment.
**v2.3.0 "Insight"**: ✅ COMPLETE — diagnostics expansion.

**Project state**: Stable and actively executing v2.6.0 workflow.

## Known Issues

- Local pytest may warn about unknown `timeout` option when `pytest-timeout` plugin is unavailable in the current environment.
