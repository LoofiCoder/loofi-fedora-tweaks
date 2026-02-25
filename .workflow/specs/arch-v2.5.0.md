# Architecture Spec — v2.5.0 "API Migration Slice 1"

## Design Rationale

v2.5.0 begins Phase 2 of the refactor plan by reducing CLI scraping reliance in
network and firewall paths while preserving the daemon-first service contracts
introduced in v2.4.0.

This slice is intentionally narrow:

1. Keep service method signatures stable for UI/CLI/API callers.
2. Replace fragile parsing paths where direct API-backed behavior is available.
3. Preserve safe fallback behavior in `LOOFI_IPC_MODE=preferred`.

## Scope

1. Network slice: reduce direct parsing-heavy execution paths in
   `services/network/network.py` and align daemon handler contracts.
2. Firewall slice: reduce parsing-heavy execution paths in
   `services/security/firewall.py` and align daemon handler contracts.
3. Update daemon handlers and focused IPC tests for network/firewall behavior.

## Non-Goals

1. Package manager API migration (`dnf`/Flatpak) in this version.
2. Full `systemctl` → D-Bus migration in this version.
3. Polkit policy audit completion in this version.

## Interfaces and Compatibility

- D-Bus daemon contract remains:
  - Bus: `org.loofi.FedoraTweaks.Daemon`
  - Object: `/org/loofi/FedoraTweaks/Daemon`
  - Interface: `org.loofi.FedoraTweaks.Daemon1`
- Envelope remains unchanged:
  - `{"ok": bool, "data": any, "error": {"code": str, "message": str} | null}`
- Existing service signatures and return shapes remain backward-compatible.

## Security and Reliability Constraints

1. No `shell=True` usage.
2. All subprocess invocations retain explicit `timeout`.
3. Validators remain the boundary for privileged or mutation actions.
4. Prefer restrictive behavior on unknown or malformed daemon payloads.
