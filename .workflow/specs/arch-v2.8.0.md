# Architecture Spec — v2.8.0 "API Migration Slice 4 (Policy & Validator Hardening)"

## Design Rationale

v2.8.0 activates the bounded Phase 3 preparation backlog from v2.7.0 by
implementing policy inventory and validator hardening for privileged pathways.
The scope is defensive and restrictive: improve validation guarantees and
traceability without broadening root-level capability.

## Scope

1. Build a policy-action inventory map from `config/*.policy`.
2. Correlate privileged daemon/API pathways with current validator coverage.
3. Tighten high-priority validator schemas and fail-closed handling.
4. Add targeted regression tests for malformed payloads and deny-by-default behavior.

## Non-Goals

1. New privileged capabilities or policy-action expansion.
2. UI feature work not required by validator hardening.
3. Broad refactors outside policy/validator pathways.

## Design Decisions

### D1: Inventory-first hardening workflow

- **Layer**: daemon + services/ipc + docs/workflow
- **New files**: optional generated inventory artifact under `.workflow/specs/` or docs
- **Modified files**: `config/org.loofi.fedora-tweaks*.policy`, `loofi-fedora-tweaks/daemon/validators.py`, selected daemon handlers
- **Pattern**: enumerate first, tighten second, test third
- **Risk**: over-hardening may reject valid payloads; mitigated with compatibility-focused regression tests

### D2: Validator tightening must remain compatibility-safe

- **Layer**: services/ipc + daemon handlers
- **Modified files**: `loofi-fedora-tweaks/services/ipc/types.py`, `loofi-fedora-tweaks/daemon/validators.py`, handler input-validation points
- **Pattern**: typed errors + envelope-safe failures
- **Risk**: caller-facing breakage; mitigated by preserving envelope contracts and required/preferred semantics

### D3: Concrete hardening targets for this slice

- **Layer**: daemon handlers + validators
- **Target handlers**: `daemon/handlers/network_handler.py`, `daemon/handlers/firewall_handler.py`, `daemon/handlers/package_handler.py`, `daemon/handlers/service_handler.py`
- **Validator module**: `daemon/validators.py`
- **Data model**: retain existing envelope contract `{"ok": bool, "data": any, "error": {"code": str, "message": str} | null}`
- **Error behavior**: malformed privileged inputs mapped to typed, fail-closed errors consumable by `services/ipc/errors.py`
- **Risk**: inconsistent parameter validation across handlers; mitigated by shared validator helpers and cross-handler tests

## Security and Reliability Constraints

1. No `shell=True` usage.
2. All subprocess calls retain explicit `timeout`.
3. No expansion of privileged action surface area.
4. Unknown/malformed privileged parameters fail closed with typed errors.
5. CI and workflow gates remain restrictive by default.

## Test Strategy

1. Add malformed payload tests for prioritized privileged actions in each targeted handler family.
2. Verify deny-by-default behavior for unsupported/invalid parameter combinations.
3. Preserve expected IPC envelope behavior for required/preferred modes through `services/ipc/daemon_client.py`.
4. Keep regression scope focused on touched validator pathways in `daemon/validators.py`.
