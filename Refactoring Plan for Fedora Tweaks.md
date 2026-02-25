# Refactoring Plan for Fedora Tweaks

Markdown

\# Persona: Expert Software Architect  
\# Task: Execute an architectural refactoring of loofi-fedora-tweaks  
\# Context: The application is a system utility for Fedora Linux. It currently suffers from performance issues (heavy Python GUI mixed with system services), instability (reliance on CLI scraping instead of APIs), and security/maintenance risks tied to scope creep and Polkit management.  
\# Format: Step-by-step implementation plan

\#\# Objective  
Transform the application into a stable, secure, and memory-efficient architecture by separating the frontend from background processes, replacing fragile CLI calls with robust APIs, and hardening the system's security model.

\---

\#\# Phase 1: Architectural Separation (Daemonization)  
Goal: Decouple heavy system calls and monitoring from the Python/PyQt interface.

1\. \*\*Create a Standalone Background Service:\*\*  
   \* Create a new \`daemon/\` directory in the root.  
   \* Implement a background daemon (preferably in Rust or C for low memory footprint, or a minimal, strictly isolated Python service without UI dependencies).  
   \* Move logic from \`core/workers/\` and the most resource-intensive files in \`services/\` (e.g., \`services/system/monitor.py\`, \`services/hardware/temperature.py\`) to the daemon.  
2\. \*\*Implement IPC (Inter-Process Communication):\*\*  
   \* Set up D-Bus or a local Unix socket for communication between the GUI (\`ui/\`) and the daemon.  
   \* Update the Python services (\`services/\`) to function primarily as IPC clients requesting data/actions from the daemon instead of executing system commands directly.

\#\# Phase 2: Replace CLI Scraping with APIs  
Goal: Eliminate fragile text parsing that breaks upon OS formatting changes.

1\. \*\*Network Management:\*\*  
   \* Locate calls to \`nmcli\`, \`ip\`, or \`firewall-cmd\` in \`services/network/\` and \`services/security/firewall.py\`.  
   \* Replace these with direct D-Bus calls to NetworkManager and the firewalld D-Bus API, or use their official Python bindings.  
2\. \*\*Package Management:\*\*  
   \* Analyze \`services/software/\` and \`services/package/\`.  
   \* Replace text parsing of \`dnf\` and \`flatpak\` output. Use the DNF Python API (\`dnf\` or \`dnf5\` module) and Flatpak's system library (\`gi.repository.Flatpak\`).  
3\. \*\*System Services:\*\*  
   \* Replace calls to \`systemctl\` with D-Bus calls to \`org.freedesktop.systemd1\`.

\#\# Phase 3: Polkit Security Hardening  
Goal: Ensure the principle of least privilege for \`org.loofi.fedora-tweaks.\*.policy\`.

1\. \*\*Validation in the IPC Layer:\*\*  
   \* Modify the daemon (from Phase 1\) to rigorously validate all incoming parameters from the GUI before executing any action requiring root privileges. No raw strings from the interface should be passed directly to a system shell.  
2\. \*\*Audit Policy Files:\*\*  
   \* Review all files in \`config/\` (e.g., \`org.loofi.fedora-tweaks.kernel.policy\`). Verify that permissions only apply to the exact binaries or methods required.

\#\# Phase 4: Version and Environment Guardrails  
Goal: Prevent application crashes following OS updates.

1\. \*\*Version Validation:\*\*  
   \* Create a new file \`core/compat\_check.py\`.  
   \* Implement functions to check the system's version of critical dependencies (e.g., KWin, Wayland, systemd) at startup.  
2\. \*\*Graceful Degradation:\*\*  
   \* Configure the UI to disable (grey out) specific tabs or features (e.g., \`ui/desktop\_tab.py\` for window management) if an unsupported version of an underlying component is detected.

\#\# Phase 5: Scope Reduction  
Goal: Reduce technical debt by removing peripheral functionality from the core application.

1\. \*\*Isolate Experimental Modules:\*\*  
   \* Move heavy, advanced, and non-standard logic (e.g., \`services/network/mesh.py\`, AI lab in \`plugins/ai\_lab/\`, virtualization in \`services/virtualization/\`) into standalone, optional plugins.  
   \* These should not be loaded into memory by default, only if explicitly installed/activated by the user.

\---  
\*\*Instructions for AI:\*\* Acknowledge that you have read and understood this plan. Ask me which phase we should begin with before generating any code.  

## Refactor Progress Snapshot (2026-02-25)

Current position in plan:

- Phase 1 (Architectural Separation / Daemonization): **Completed** in v2.4.0 Phase 1 scope.
- Phase 2 (Replace CLI scraping with APIs): **In progress** (v2.5.0 and v2.6.0 slices completed for network/firewall/packages).
- Phase 3 (Polkit security hardening): **Partially addressed** via daemon validators; policy audit remains.
- Phase 4 (Version and environment guardrails): **Not started**.
- Phase 5 (Scope reduction / optionalization): **Not started**.

What was completed for Phase 1:

- Added daemon package and runtime entrypoint (`--daemon`) with D-Bus host and contracts.
- Added strict request validators and structured error envelope handling.
- Added IPC client layer with `disabled|preferred|required` mode semantics.
- Migrated network/firewall/ports services to daemon-first with fallback (`LOOFI_IPC_MODE=preferred`).
- Routed security UI firewall actions through service layer.
- Added/updated IPC tests and packaging/runtime docs for v2.4.0.

Immediate next step:

- Continue Phase 2 with a service/systemctl migration slice while pairing the design with bounded Phase 3 preparation tasks (policy inventory + validator tightening plan).
