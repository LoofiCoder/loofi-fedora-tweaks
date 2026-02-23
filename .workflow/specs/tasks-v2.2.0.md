# Tasks for v2.2.0 "Velocity" — Performance & Stability

> Theme: Performance caching, subprocess safety, service-layer test coverage
> Generated: 2026-02-23

| #   | Task                                               | Agent            | Layer          | Size | Depends | Files                                                                                                                         | Done |
| --- | -------------------------------------------------- | ---------------- | -------------- | ---- | ------- | ----------------------------------------------------------------------------------------------------------------------------- | ---- |
| 1   | Version bump to 2.2.0 "Velocity"                   | code-implementer | core           | S    | -       | version.py, pyproject.toml, .spec, .race-lock.json                                                                            | [x]  |
| 2   | Add timeout to 17 subprocess.run() calls           | backend-builder  | services/utils | M    | -       | agent_runner.py, ai.py, kwin.py, battery.py, mesh.py, disposable_vm.py, containers.py, focus_mode.py, smart_logs.py, voice.py | [x]  |
| 3   | Create \_cached_which() utility                    | backend-builder  | utils          | S    | -       | utils/system.py (or new utils/cached_tools.py)                                                                                | [x]  |
| 4   | Migrate shutil.which() → \_cached_which() codebase | backend-builder  | services/utils | L    | 3       | ~30 files across services/, utils/, core/                                                                                     | [x]  |
| 5   | Cache SystemManager static methods                 | backend-builder  | utils          | S    | -       | utils/system.py                                                                                                               | [x]  |
| 6   | Cache static subprocess data                       | backend-builder  | services/utils | M    | -       | system_info_utils.py, journal.py, ai.py, virtualization.py, kickstart.py, firewall.py                                         | [x]  |
| 7   | Replace print() with logger in plugins             | code-implementer | core           | S    | -       | core/plugins/package.py, core/plugins/scanner.py                                                                              | [x]  |
| 8   | Tests for subprocess timeout additions             | test-writer      | tests          | M    | 2       | tests/test_timeout_enforcement.py                                                                                             | [x]  |
| 9   | Tests for \_cached_which utility                   | test-writer      | tests          | S    | 3       | tests/test_cached_which.py                                                                                                    | [x]  |
| 10  | Service layer tests: desktop + hardware            | test-writer      | tests          | L    | -       | tests/test_service_desktop.py, tests/test_service_hardware.py                                                                 | [x]  |
| 11  | Service layer tests: security + network + virt     | test-writer      | tests          | L    | -       | tests/test_service_security.py, tests/test_service_network.py, tests/test_service_virtualization.py                           | [x]  |
| 12  | Update CHANGELOG, README, release notes            | release-planner  | docs           | S    | 1–11    | CHANGELOG.md, README.md, docs/releases/RELEASE-NOTES-v2.2.0.md                                                                | [x]  |
| 13  | Full verification (tests, lint, coverage)          | test-writer      | all            | S    | 1–12    | -                                                                                                                             | [x]  |

---

## Acceptance Criteria

### TASK-01: Version bump to 2.2.0 "Velocity"

- `version.py`: `__version__ = "2.2.0"`, `__version_codename__ = "Velocity"`
- `pyproject.toml`: `version = "2.2.0"`
- `.spec`: `Version: 2.2.0`
- `.race-lock.json`: `"version": "v2.2.0"`, `"status": "active"`
- All three version sources match

### TASK-02: Add timeout to 17 subprocess.run() calls

- Every `subprocess.run()` call in codebase has `timeout=N` parameter
- Files: `agent_runner.py` L464, `ai.py` L426, `kwin.py` L101/L143/L232/L277, `battery.py` L93, `mesh.py` L143, `disposable_vm.py` L75/L121, `containers.py` L332, `focus_mode.py` L452/L471/L499, `smart_logs.py` L351, `voice.py` L253/L274
- Timeout values appropriate per operation (15s for quick checks, 60s for installs, 120s for builds)
- No regressions in existing tests

### TASK-03: Create \_cached_which() utility

- New function `_cached_which(tool: str) -> Optional[str]` with `@lru_cache(maxsize=64)`
- Located in `utils/system.py` or new `utils/cached_tools.py`
- Documented with docstring
- Import-ready for all consumers

### TASK-04: Migrate shutil.which() → \_cached_which()

- All `shutil.which()` calls across `services/`, `utils/`, `core/` replaced with `_cached_which()`
- ~100+ callsites updated across ~30 files
- Worst offenders: `services/hardware/hardware.py` (18), `services/virtualization/vm_manager.py` (10), `utils/clipboard_sync.py` (8), `utils/voice.py` (7)
- No behavioral change — only performance improvement
- All existing tests still pass

### TASK-05: Cache SystemManager static methods

- `SystemManager.is_atomic()` cached with `@lru_cache`
- `SystemManager.get_package_manager()` cached with `@lru_cache`
- Other static-data methods cached where appropriate
- Cache doesn't change during app lifetime (OS doesn't switch atomic ↔ traditional mid-session)

### TASK-06: Cache static subprocess data

- One-shot system queries cached for session lifetime:
  - `lscpu` output (system_info_utils.py)
  - `uname -r` output (journal.py)
  - `lspci` output (ai.py, virtualization.py)
  - `localectl status` output (kickstart.py)
  - `firewall-cmd --version` output (firewall.py)
- Cache invalidation: none needed (static per session)
- Wrap in helper or use `@lru_cache` on calling methods

### TASK-07: Replace print() with logger in plugins

- `core/plugins/package.py` L59: `print()` → `logger.info()` or `logger.debug()`
- `core/plugins/scanner.py` L23: `print()` → `logger.info()` or `logger.debug()`
- Add `logger = logging.getLogger(__name__)` if missing

### TASK-08: Tests for subprocess timeout enforcement

- Verify all 17 fixed callsites have timeout parameter
- Test that `subprocess.TimeoutExpired` is handled gracefully
- Use `@patch` decorators, mock subprocess calls

### TASK-09: Tests for \_cached_which utility

- Test cache hit/miss behavior
- Test with existing tool (returns path)
- Test with missing tool (returns None)
- Test cache is shared across calls
- Test `@lru_cache` stats if applicable

### TASK-10: Service layer tests — desktop + hardware

- `tests/test_service_desktop.py` — tests for `services/desktop/desktop.py`, `display.py`, `kwin.py`
- `tests/test_service_hardware.py` — tests for `services/hardware/hardware.py`, `battery.py`, `disk.py`, `temperature.py`, `hardware_profiles.py`
- All system calls mocked with `@patch`
- Success and failure paths tested

### TASK-11: Service layer tests — security + network + virtualization

- `tests/test_service_security.py` — tests for `services/security/firewall.py`, `secureboot.py`
- `tests/test_service_network.py` — tests for `services/network/network.py`, `mesh.py`
- `tests/test_service_virtualization.py` — tests for `services/virtualization/vm_manager.py`
- `tests/test_service_package.py` — tests for `services/package/base.py`, `service.py`
- All system calls mocked, both success/failure paths

### TASK-12: Update CHANGELOG, README, release notes

- `CHANGELOG.md` entry for v2.2.0 with all changes categorized
- `README.md` version badge updated if applicable
- `docs/releases/RELEASE-NOTES-v2.2.0.md` scaffolded via `bump_version.py`
- Mention: timeout enforcement, caching layer, service-layer test expansion

### TASK-13: Full verification

- `python -m pytest tests/ -v --cov=loofi-fedora-tweaks --cov-fail-under=80`
- `flake8 loofi-fedora-tweaks/ --max-line-length=150`
- No regressions, coverage ≥ 80%

---

## Research Data (from codebase analysis)

### Subprocess calls missing timeout (17)

| File                                     | Line                   |
| ---------------------------------------- | ---------------------- |
| core/agents/agent_runner.py              | L464                   |
| core/ai/ai.py                            | L426                   |
| services/desktop/kwin.py                 | L101, L143, L232, L277 |
| services/hardware/battery.py             | L93                    |
| services/network/mesh.py                 | L143                   |
| services/virtualization/disposable_vm.py | L75, L121              |
| utils/containers.py                      | L332                   |
| utils/focus_mode.py                      | L452, L471, L499       |
| utils/smart_logs.py                      | L351                   |
| utils/voice.py                           | L253, L274             |

### Uncached shutil.which() — top offenders

| File                                      | Calls |
| ----------------------------------------- | ----- |
| services/hardware/hardware.py             | ~18   |
| services/virtualization/vm_manager.py     | ~10   |
| utils/clipboard_sync.py                   | ~8    |
| services/virtualization/virtualization.py | ~7    |
| utils/voice.py                            | ~7    |
| core/ai/ai.py                             | ~6    |
| services/virtualization/disposable_vm.py  | ~5    |
| utils/wizard_health.py                    | ~4    |

### Services without direct test files (18)

desktop.py, display.py, kwin.py, battery.py, disk.py, hardware_profiles.py,
hardware.py, temperature.py, mesh.py, network.py, base.py (package),
service.py (package), firewall.py, secureboot.py, flatpak.py, processes.py,
system.py, vm_manager.py
