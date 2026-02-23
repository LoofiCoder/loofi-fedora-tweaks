# Release Notes — v2.2.0 "Velocity"

**Release Date:** 2026-02-23  
**Type:** Performance & Stability  
**Status:** IN PROGRESS

## Overview

v2.2.0 "Velocity" is a performance and stability release focused on eliminating redundant system calls, caching static data, and expanding service-layer test coverage. No new user-facing features — the app is faster and more reliable.

## Deliverables

### ✅ Performance — cached_which()

- Created `cached_which()` in `services/system/system.py` — `@lru_cache(maxsize=64)` wrapper around `shutil.which()`
- Migrated **132 `shutil.which()` calls across 44 files** to use the cached version
- Eliminates ~2-5ms per lookup on subsequent calls (PATH scanning is surprisingly expensive)

### ✅ Performance — Static Subprocess Caching

- `get_cpu_model()` — `@lru_cache(maxsize=1)` (lscpu output doesn't change per session)
- `_get_lspci_output()` — cached lspci output for AMD GPU detection in AI module
- `_cached_keyboard_layout()` — cached localectl status for Kickstart generator
- `FirewallManager.is_available()` — class-level `_available_cached` variable

### ✅ SystemManager Caching

- Verified `is_atomic()` already cached via `_is_atomic_cached` class variable
- Updated `is_flatpak_available()` to use `cached_which("flatpak")` instead of raw `shutil.which()`

### ✅ Service Layer Tests — 215 New Tests

| Test File | Tests | Modules Covered |
|-----------|-------|-----------------|
| `test_cached_which.py` | 7 | cached_which utility |
| `test_service_desktop.py` | 52 | WaylandDisplayManager, KWinManager |
| `test_service_hardware.py` | 45 | BatteryManager, DiskManager, TemperatureManager |
| `test_service_security.py` | 31 | FirewallManager, SecureBootManager |
| `test_service_network.py` | 22 | NetworkUtils |
| `test_service_virtualization.py` | 28 | VMManager |
| `test_service_package.py` | 30 | DnfPackageService, RpmOstreePackageService |

## What's Changed

### Files Modified (Performance)

- `services/system/system.py` — added `cached_which()` function
- `utils/system_info_utils.py` — `@lru_cache` on `get_cpu_model()`
- `core/ai/ai.py` — `_get_lspci_output()` cached helper
- `core/export/kickstart.py` — `_cached_keyboard_layout()` cached helper
- `services/security/firewall.py` — `_available_cached` class variable
- 44 files migrated from `shutil.which()` to `cached_which()`

### Files Created (Tests)

- `tests/test_cached_which.py`
- `tests/test_service_desktop.py`
- `tests/test_service_hardware.py`
- `tests/test_service_security.py`
- `tests/test_service_network.py`
- `tests/test_service_virtualization.py`
- `tests/test_service_package.py`

## Upgrade Notes

- No breaking changes — all changes are internal performance optimizations
- No new dependencies
- No configuration changes required

