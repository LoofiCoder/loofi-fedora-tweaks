# Release Notes — v2.11.0

## Highlights

- Network local write paths now enforce strict success/failure semantics based on subprocess exit codes.
- Active connection detection is hardened to deterministic parsing for wifi/ethernet rows.
- Firewall local mutators and reload behavior are normalized to centralized `PrivilegedCommand` tuple construction.
- Privileged firewall actions are aligned with project audit expectations (action, params, exit code).
- Read-path contracts are explicitly classified for `get_available_services()`, `has_pending_deployment()`, and `get_layered_packages()`.
- No new UI tabs or CLI commands; improved reliability of network/firewall operation results.
- `pkexec`-only privilege model is preserved; no `sudo` or `shell=True` usage introduced.
- Explicit `timeout` remains required on all touched subprocess paths; no package-manager hardcoding.

## Upgrade Notes

- No breaking changes; method signatures and return types remain backward compatible.
- D-Bus envelope and IPC fallback semantics remain unchanged.
- Read-path decisions avoid privilege-scope expansion and keep safe defaults (`[]`/`False`/`None`).

## Validation Commands

- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_network_utils.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_service_network.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_ipc_fallback_modes.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_firewall_manager.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_service_security.py -v`
- `PYTHONPATH=loofi-fedora-tweaks python -m pytest tests/test_system_service.py -v`

## Critical Rules Introduced

- Hardened privilege model: only `pkexec` via `PrivilegedCommand`, never `sudo` or `shell=True`.
- All subprocess calls must include explicit `timeout` parameter.
- No package-manager hardcoding; always use `SystemManager.get_package_manager()`.
- Audit log required for all privileged actions (timestamp, action, params, exit code).

---

For full details, see the [CHANGELOG.md](../../CHANGELOG.md) and [ROADMAP.md](../../ROADMAP.md).

