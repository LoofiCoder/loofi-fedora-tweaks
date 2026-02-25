# Architecture Spec — v2.7.0 "API Migration Slice 3 (System Services)"

## Design Rationale

v2.7.0 continues Phase 2 of the refactor plan by extending daemon-first migration
into system/service operations while preserving caller contracts and preferred-mode
fallback behavior introduced in prior slices.

This slice also includes bounded Phase 3 preparation by documenting policy-audit and
validator-tightening scope without introducing new root-level capabilities.

## Scope

1. Add daemon handler support for system/service operations under `daemon/handlers/`.
2. Migrate targeted pathways in `services/system/service.py` to prefer daemon/API-backed execution.
3. Preserve strict IPC envelope compatibility and fallback semantics in `services/ipc/`.
4. Define a Phase 3 prep checklist (policy inventory + validator tightening) as planning artifacts only.

## Non-Goals

1. Broad UI feature expansion unrelated to system/service migration.
2. Full policy rewrite or privilege model expansion in this version.
3. Packaging/release automation changes unrelated to slice-3 migration.

## Interfaces and Compatibility

- D-Bus daemon contract remains:
  - Bus: `org.loofi.FedoraTweaks.Daemon`
  - Object: `/org/loofi/FedoraTweaks/Daemon`
  - Interface: `org.loofi.FedoraTweaks.Daemon1`
- Envelope remains unchanged:
  - `{"ok": bool, "data": any, "error": {"code": str, "message": str} | null}`
- Existing `SystemService` method signatures remain backward-compatible for callers.
- `LOOFI_IPC_MODE=preferred` remains the default resilience mode.

## Design Decisions

### D1: Service handler parity with existing daemon handler patterns

- **Layer**: daemon + services + ipc
- **New files**: `loofi-fedora-tweaks/daemon/handlers/service_handler.py`
- **Modified files**: `loofi-fedora-tweaks/daemon/handlers/__init__.py`, `loofi-fedora-tweaks/services/system/service.py`, `loofi-fedora-tweaks/services/ipc/daemon_client.py`, `loofi-fedora-tweaks/services/ipc/types.py`
- **Pattern**: align with `network_handler.py`, `firewall_handler.py`, `package_handler.py`
- **Risk**: inconsistent payload parsing could break fallback; mitigated by strict schema checks and typed errors

### D2: Bounded Phase 3 preparation with restrictive defaults

- **Layer**: planning/docs only
- **Modified files**: `.workflow/specs/tasks-v2.7.0.md`, `ROADMAP.md`
- **Pattern**: preparation-only checklist, no runtime privilege expansion
- **Risk**: accidental scope creep; mitigated by explicit non-goals and hardening-gate references

## Security and Reliability Constraints

1. No `shell=True` usage.
2. All subprocess invocations retain explicit `timeout`.
3. Privileged pathways continue using `PrivilegedCommand` and strict validation.
4. Unknown or malformed daemon payloads fail closed with typed errors.
5. Phase 3 prep must remain documentation/planning unless explicitly activated in a future active slice.

## Phase 3 Preparation Checklist (Bounded)

References:

- `.github/instructions/system_hardening_and_stabilization_guide.md` (Phase 2 and Phase 3 constraints)

Inventory tasks for next activation slice:

- Build a policy inventory table for `config/org.loofi.fedora-tweaks.*.policy` containing action id, required privilege scope, and linked capability/caller path.
- Map daemon-exposed privileged methods to validator coverage and identify missing schema validation.
- Confirm each privileged pathway enforces explicit allowlist behavior, structured audit logging, and rollback or dry-run strategy where mutation occurs.
- Verify API exposure constraints remain restrictive (`127.0.0.1` default bind and explicit `--unsafe-expose` gate for non-localhost use).
- Define acceptance gates for Phase 3 activation: no new root capability expansion, no unvalidated privileged parameters, and documentation parity across architecture/workflow/hardening docs.

## Test Strategy

1. Extend `tests/test_daemon_client.py` with service-handler payload success/failure cases.
2. Extend `tests/test_ipc_fallback_modes.py` for preferred/required behavior on service operations.
3. Extend `tests/test_system_service.py` for daemon-first parity and fallback semantics.
4. Preserve compatibility expectations for existing callers and return types.

