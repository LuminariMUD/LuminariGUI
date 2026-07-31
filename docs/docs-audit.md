# Comprehensive Documentation Audit Plan

This document outlines the multi-phase plan to audit, update, and complete the documentation for the LuminariGUI project. Each phase is scoped to be achievable in a single development session.

## Phase 1: Foundation & Entry Points
**Goal:** Establish the documentation structure and ensure the project has a clear entry point.
- [x] **Create/Update Root README.md**:
    - [x] Project overview and features.
    - [x] Installation instructions (importing `LuminariGUI.xml`).
    - [x] Quick start guide.
    - [x] Links to other documentation files.
- [x] **Audit Directory Structure**:
    - [x] Review `docs/` folder organization.
    - [x] Ensure `LICENSE` file is accurate and referenced.
- [x] **Initial Assessment**:
    - [x] Verify all markdown links in existing docs are valid.
    - [x] Identify obsolete files.

## Phase 2: Developer Tooling & Workflow
**Goal:** Document the development ecosystem, specifically the Python automation tools.
- [x] **Audit `docs/PYTHON_TOOLS.md`**:
    - [x] Verify instructions for `run_tests.py`, `validate_package.py`, `create_package.py`, etc.
    - [x] Ensure dependency requirements are listed (e.g., `requirements.txt` check).
    - [x] Document usage of `scripts/` folder contents.
- [x] **Audit `docs/MUDLET_DEVELOPMENT.md`**:
    - [x] Update workflow for editing `LuminariGUI.xml`.
    - [x] Clarify the "Single File vs. Split Scripts" architecture.
    - [x] Add guidelines for XML/Lua separation if applicable.

## Phase 3: Feature & Protocol Specifications
**Goal:** accurate documentation of the technical implementation details and user-facing features.
- [x] **Audit `docs/PROTOCOL_REFERENCE.md`**:
    - [x] Review MSDP implementation details.
    - [x] Verify variable mappings against `MSDPMapper` code in `LuminariGUI.xml`.
- [x] **Audit `docs/SOUND_USAGE.md`**:
    - [x] specific sound triggers and configuration.
    - [x] Check `audio/` directory structure against documentation.
- [x] **Audit `images/affected_by/STATUS_EFFECTS.md`**:
    - [x] Ensure status icons match the documentation.
    - [x] Update visual references if necessary.

## Phase 4: Codebase & Inline Documentation
**Goal:** Ensure the code itself is self-documenting and follows the style guide.
- [x] **Lua Script Analysis**:
    - [x] Review `LuminariGUI.xml` for comment quality in major script blocks (MSDPMapper, GUI, YATCO).
    - [x] Check function headers for inputs/outputs.
- [x] **Python Script Analysis**:
    - [x] Check docstrings in `scripts/*.py`.
    - [x] Ensure all script arguments are documented (`--help` output vs docs).
- [x] **Style Compliance**:
    - [x] Cross-check against naming conventions in `MUDLET_DEVELOPMENT.md`.

## Phase 5: Maintenance & Process
**Goal:** Standardize how changes and tasks are tracked.
- [x] **Audit `docs/CHANGELOG.md`**:
    - [x] Ensure consistent format (Keep a Changelog standard).
    - [x] Consolidate or archive `docs/previous_changelogs/` if needed.
- [x] **Audit `docs/TASK_LIST.md`**:
    - [x] Update current status of tasks.
    - [x] Remove completed items or move to historical log.
- [x] **Contribution Guide**:
    - [x] Create or update guidelines for submitting PRs/Issues (can be part of README or separate `CONTRIBUTING.md`).

## Phase 6: Mudlet Version Compatibility (2026-07-31)
**Goal:** Document what changed in Mudlet 4.20–4.22 so the package can be audited and fixed against the current client.
- [x] **Research upstream changes**:
    - [x] Review Mudlet 4.20, 4.21, 4.22 release notes and relevant PRs.
    - [x] Identify open upstream bugs affecting Geyser/miniconsole/resize behaviour.
- [x] **Create `docs/MUDLET_COMPATIBILITY.md`**:
    - [x] Version-by-version breakdown filtered to changes affecting this package.
    - [x] Known open upstream bugs, LuminariGUI-specific audit findings, triage checklist, sources.
- [x] **Correct `docs/MUDLET_DEVELOPMENT.md`**:
    - [x] Replace the obsolete "single-file architecture" section with the source-to-build system.
    - [x] Fix stale tool references (`scripts/create_package.py` → `theGUI/package.py`).
    - [x] Add Qt stylesheet, label callback, resize handling, and `sysLoadEvent` flag guidance.
    - [x] Add authoritative `config.lua` field list from Mudlet's exporter.
- [x] **Cross-link**: README and `PROTOCOL_REFERENCE.md` MSDP troubleshooting.

### Phase 6 follow-up (code) — completed 2026-07-31 in v2.0.4.028
Tracked in the "Audit Findings" section of `MUDLET_COMPATIBILITY.md`:
- [x] Replace legacy string-name `setClickCallback` calls with closures.
- [x] Remove unsupported `box-shadow` declarations from stylesheets (also `text-shadow` in QSS).
- [x] Fix `config.lua` `dependencies` to be a comma-separated string; add `helpURL`; drop non-standard `modified`.
- [x] Raise the stale `mudlet_version = "4.0+"` declaration to a realistic minimum (`4.21+`).
- [x] Use the `sysLoadEvent` fresh-load/reset boolean to re-subscribe to MSDP after `resetProfile()`.
- [x] **Found during the fix pass:** eliminate the event-handler leak and six duplicate registrations.
- [x] Remove obsolete `tests/test_state_validation.py`; it targeted a nonexistent "State Validator" subsystem and always failed standalone.

Deliberately left open:
- [ ] `icon` in `config.lua` — needs an actual 512x512 icon asset, which the repo does not have.
- [ ] Visual re-verification under Qt6 of `background` (shorthand) and `vertical-align`, which have limited QSS support.

## Execution Strategy
- Start with **Phase 1** to ensure the project is navigable.
- Proceed sequentially.
- Each phase includes a "Review & Verify" step before moving to the next.
