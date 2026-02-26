# Project Brief — Loofi Fedora Tweaks

## Overview

**Loofi Fedora Tweaks** is a desktop control center for Fedora Linux that combines maintenance, diagnostics, tuning, networking, security, and automation in one unified application. It replaces fragmented CLI tools with a cohesive GUI, CLI, daemon, and API experience.

## Core Requirements

- **Platform**: Fedora Linux (targets Fedora 43)
- **Language**: Python 3.12+
- **Framework**: PyQt6 6.7+
- **Test Coverage**: 80% minimum (CI-enforced)
- **Privilege Model**: `pkexec` only — never `sudo`
- **Atomic Support**: Branch on `SystemManager.is_atomic()` for dnf vs rpm-ostree

## Scope

- **28 feature tabs** organized into 7 categories (System, Hardware, Network, Desktop, Security, Software, Advanced)
- **4 entry modes**: GUI (default), CLI (`--cli`), Daemon (`--daemon`), API (`--api`)
- **107 utils modules** — shared business logic consumed by all entry modes
- **9 service domains**: security, hardware, network, desktop, software, storage, virtualization, system, package
- **8 core domains**: agents, ai, diagnostics, export, executor, plugins, profiles, workers
- **228+ test files** with 6383+ tests

## Goals

1. Unified Fedora system management — one app for all system tasks
2. Safety-first design — confirmation dialogs, audit logging, rollback strategies
3. Support both traditional Fedora (dnf) and Atomic Fedora (rpm-ostree)
4. Plugin ecosystem with marketplace, sandboxing, and integrity checks
5. Multiple access modes (GUI, CLI, API, Daemon) sharing the same business logic

## Distribution

- RPM via COPR (`loofitheboss/loofi-fedora-tweaks`)
- Flatpak (org.loofi.FedoraTweaks)
- AppImage
- Direct install via `install.sh`

## Current Version

**v2.8.0 "API Migration Slice 4"** — Policy inventory execution + validator hardening (SemVer)
