# Release Notes — Loofi Fedora Tweaks v4.0.0 "Atlas"

## Theme: Guided Fedora Control Center

v4.0.0 "Atlas" transforms Loofi Fedora Tweaks from a comprehensive toolbox into a guided system assistant. This release focuses on proactive health monitoring, safe repair workflows, and a streamlined task-based user experience.

### Key Pillars

#### 1. Health & Repair Autopilot
- **Proactive Checks**: Automatically detects common Fedora issues (failed services, DNF locks, broken repos, SELinux warnings).
- **Structured Recommendations**: Each health finding includes a severity level, an explanation of the risk, and a suggested safe fix.
- **Safety First**: Non-destructive by default. Provides manual commands and documentation links for all identified issues.

#### 2. Rollback-First Action Model
- **Dry-Run Support**: Preview system changes before they are applied.
- **Risk Assessment**: Every operation is classified by risk level (Info, Low, Medium, High).
- **Preflight Checks**: Validates system state (disk space, locks, dependencies) before allowing mutations.
- **Revert Hints**: Provides clear instructions on how to undo or rollback changes where practical.

#### 3. Fedora Upgrade Assistant
- **Readiness Audit**: Comprehensive check before performing a major Fedora version upgrade.
- **Dependency Scan**: Detects third-party repositories (COPR, RPM Fusion) and drivers (NVIDIA/akmods) that may impact upgrade success.
- **Resource Verification**: Ensures sufficient disk space and kernel stability before recommending an upgrade path.

#### 4. Task-Based Home UX
- **Dashboard Cards**: Direct access to high-value system tasks like "Maintain my system", "Fix problems", and "Prepare upgrade".
- **Visual Health Score**: At-a-glance status of system health, security, and performance.

#### 5. Atomic Fedora (rpm-ostree) First-Class Support
- **Full Parity**: Health checks and upgrade assistance tailored for Atomic Fedora variants (Silverblue, Kinoite, etc.).
- **Overlay Detection**: Specialized reporting for layered packages and system overrides.

### Implementation Status: Foundation Phase
This release establishes the core backend schemas, structured models, and architectural boundaries for the Atlas vision.

- [x] Health & Repair Autopilot Foundation
- [x] Rollback-First Action Metadata
- [x] Fedora Upgrade Assistant Foundation
- [x] Task-Based Home UX Foundation
- [x] Support Bundle v2
