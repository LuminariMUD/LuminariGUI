# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Historical entries through v2.0.4.016 are preserved in
[`HISTORICAL_CHANGELOG.md`](HISTORICAL_CHANGELOG.md).

---
Begin Changelog entries below
---

## [Unreleased]

### Added

- **Composite GUI source assembly.** `theGUI/src/scripts/01_gui.xml` is now a
  small ordered wrapper over independently valid fragments in
  `theGUI/src/scripts/gui/`. The builder resolves explicit nested includes,
  rejects missing, invalid, cyclic, traversing, and out-of-root includes, and
  reports included files in stats/watch mode without leaking build directives
  into the Mudlet package.
- **Focused GUI scripts.** The former `MSDP` and `Config` nodes are split into
  protocol, gauge, action, boot, event-registry, refresh, and lifecycle nodes;
  the wrapper is under 100 lines and every child remains under 300 Lua lines.
- **End-to-end screen diagnostic mode.** A first-loaded debug bootstrap exposes
  one master `GUI.DEBUG` switch, disabled by default, and emits copyable
  `LGUI-DEBUG`, `LGUI-ERROR`, and `LGUI-TRACE` output in Mudlet's main
  console. Instrumentation covers boot stages, lifecycle events, MSDP
  subscriptions and values, handler registration/invocation, GUI components,
  mapper activity, adjustable containers, YATCO/chat, triggers, aliases, keys,
  assets, and runtime snapshots.
- **Fault-safe startup tracing.** The three GUI calls that run before
  `GUI.initializeOrRefresh` and the YATCO configuration boundary now report
  full stack traces and allow later diagnostics to load while debug mode is
  enabled. With debugging disabled, original error propagation is preserved.
- **Central runtime resource ownership.** A first-loaded resource layer now
  provides replace-before-register handler ownership, named temporary timers,
  one-shot ID retirement, recurring-timer replacement, and complete profile
  exit/package uninstall cleanup.
- **Ownership-aware resource audit.** `scripts/analyze_handlers.py` now
  assembles current source in memory, separates runtime and package-XML
  handlers, reports named timer creation sites, supports JSON and explicit XML
  input, and fails on raw unowned registrations.
- **Scope-aware Mudlet name validation.** Final package validation now rejects
  exact same-family names only when the items are direct siblings. Group/leaf
  pairs share one family, while intentional same names in different parent
  groups or package sections remain valid and regression-covered.
- **Comprehensive continuous integration.** Hash-locked core checks, Lua 5.1
  analysis, security scanning, source-mapped Lua tooling, separate Lua/Python
  coverage, an advisory official-Mudlet launch experiment, documentation, and
  stable branch protection now form one reproducible six-phase baseline.
- **Generated XML source mapper.** `scripts/map_generated_line.py` maps any
  current `LuminariGUI.xml` line to the exact skeleton, wrapper, or recursively
  included physical fragment line, reports manifest context, emits optional
  JSON, and rejects stale generated output.
- **Composite YATCO source assembly.** The outer YATCO/Demonnic hierarchy is
  now a small ordered wrapper over independently valid Shared and Tabbed Chat
  group subtrees, without changing one byte of generated package topology or
  Lua load order.
- **Package icon.** A 512×512 compass-and-portal mark now ships in Mudlet's
  native `.mudlet/Icon/` archive layout and is declared by basename in the
  generated `config.lua`; package tests verify the asset and dimensions.
- **Native sound subsystem.** Chat, low-health, and low-movement alerts now
  share tagged Mudlet media playback, persistent per-channel switches, volume,
  files, cooldowns, low-vitals thresholds, crossing latches, a master switch,
  and the `sound` command. Two portable PCM warning cues ship with the package;
  `dsound` and `set chat sound` remain compatible delegates.

### Fixed

- **Qt6 stylesheet compatibility.** Unsupported `vertical-align` declarations
  were removed, scrollbar backgrounds now use explicit `background-color`,
  and the tabbed-info center's dynamically assembled declaration now has its
  required semicolon. Mudlet 4.22.0/Qt 6.9 runtime logs are warning-free and
  relevant before/after visual crops are pixel-identical; regression coverage
  prevents the invalid forms from returning.
- **Live monolithic-to-split upgrade lifecycle overlap.** Pre-split releases
  registered anonymous load/connection closures without retaining their IDs,
  so one legacy callback can survive an in-session replacement and run beside
  the new callback. Lifecycle registrations now have explicit ownership and
  replacement, while initialization, refresh, and REPORT requests coalesce
  that one unavoidable legacy overlap. Real Mudlet 4.22 validation confirms a
  single connection refresh and stable handler counts after upgrading from
  `2.0.4.034`.
- **`resetProfile()` nil-MSDP error.** Mudlet clears the global `msdp` table
  before emitting the reset-flavoured `sysLoadEvent`; the refresh path now
  recreates it before reading resource fields. Verified in Mudlet 4.21 and
  4.22 without a reconnect.
- **Full-screen `Legend/Room` and `Mudlet/ASCII` controls.** The immediate GUI
  bootstrap called `GUI.init_boxes()` before the AdjustableContainers
  namespace existed. Diagnostic mode caught that failure and continued into
  `GUI.buttonWindow.init()`, causing Mudlet to parent both controls to the root
  window at full size. The container foundation now loads before GUI
  construction, stale controls are removed during an in-place upgrade, and
  child initialization stops safely if any core parent is unavailable.
- **Duplicate mapper construction on connection.** Mudlet emits both
  `sysConnectionEvent` and `sysProtocolEnabled("MSDP")` during normal startup.
  Both paths requested mapper initialization, replacing the live Map and ASCII
  Map containers less than a second after creating them. Mapper setup is now
  idempotent and reuses the complete runtime created by the first event.
- **Misleading mapper diagnostics.** Runtime snapshots checked nonexistent
  `map.window` and `map.asciiwindow` fields and therefore reported both map
  views as `nil` after successful construction. They now inspect the actual
  `map.mapwindow` and `map.minimap` objects.
- **Long-lived timer and handler cleanup.** All package-created anonymous
  handlers and temporary timers now have explicit owners. Reconnect,
  `resetProfile()`, rapid refresh, sequential refresh, profile exit, and
  package uninstall no longer leave stacked or stale resource IDs.

### Changed

- **Historical changelogs consolidated.** The two legacy changelog snapshots
  now live in one `docs/HISTORICAL_CHANGELOG.md` document with their original
  filenames and introducing commit recorded for provenance.
- **Oversized mapper reviewed and bounded.** The mapper remains one script so
  its internal tables and helpers retain their private shared lexical scope;
  regression coverage caps the documented exception instead of changing
  reload semantics solely to meet an approximate physical-line target.

- **Source-aware lifecycle tests.** Tests assemble the composite source in
  memory, find Lua by Mudlet script name, enforce script order/size bounds,
  and cover lifecycle ownership, legacy callback coalescing, reset recovery,
  and real Adjustable.Container `.Inside` parenting semantics.
- **Exact lifecycle regression baseline.** Production Lua mocks and an
  isolated Mudlet 4.22 run now verify stable 5 mapper + 26 GUI + 6 lifecycle
  handlers, one bounded recurring timer, balanced refresh replacement, single
  event multiplicity, and zero owned resources after uninstall.
- **Release now means published.** `python3 theGUI/package.py release`
  atomically pushes `master`, the release branch, and annotated tag to
  `origin`, verifies each remote ref, publishes the GitHub Release page,
  uploads and verifies both release assets, and remains on `master`. Local
  artifact creation is explicitly the responsibility of `package.py create`;
  there is no commit-without-push release mode.
- **Release guidance hardened.** Agent and developer documentation now requires
  a published GitHub Release page with both the `.mpackage` and JSON metadata,
  plus remote verification, before reporting a requested release complete.
- **Project documentation consolidated.** Durable source-layout, event
  ownership, refresh, and manual-test guidance now lives in the build,
  protocol, compatibility, and development references. Unfinished work is
  centralized in `docs/ongoing-projects/TASK_LIST.md`.

### Removed

- Superseded source-build and GUI-split project plans, the completed chunk
  audit, and a one-off diagnostic console capture from
  `docs/ongoing-projects/` after their durable findings were consolidated.

## [2.0.4.028] - 2026-07-31

Mudlet 4.20–4.22 compatibility pass. Mudlet 4.20 moved to Qt6 and 4.21 changed
label/callback internals; this release adapts the package and fixes a
long-standing event-handler leak found during the audit.

### Fixed

- **Event handler leak (major).** `GUI.registerEventHandlers()` runs on every
  `GUI.init()` *and* every `GUI.initializeOrRefresh()`, but never removed the
  handlers it had previously registered. Handlers accumulated without bound:
  measured at 36 → 68 → 324 live handlers over ten refresh cycles, meaning a
  single MSDP update eventually fanned out to ~10 duplicate handlers
  (duplicate REPORT storms, redundant redraws, growing latency). The function
  now kills only the GUI handlers it owns before re-registering and is
  verifiably idempotent (flat 30 handlers across repeated calls). This
  ownership boundary preserves the reused file-scope mapper/protocol handler
  IDs during an in-place upgrade.
- **Duplicate event registrations.** `msdp.ROOM`, `shiftRoom`,
  `sysConnectionEvent`, `sysDownloadDone` (→ `map.eventHandler`) and
  `sysProtocolEnabled` (→ `map.onProtocolEnabled` and `GUI.onProtocolEnabled`)
  were registered both at file scope and again in the GUI handler tables, so
  the mapper processed every room change twice. The file-scope registrations
  are now the single source; the duplicates were removed from the tables.
- **Blank GUI after `resetProfile()`.** `sysProtocolEnabled` does not fire
  again after a profile reset (MSDP is already negotiated), so the GUI never
  re-sent its MSDP `REPORT` subscriptions and sat empty. `sysLoadEvent` now
  uses the boolean flag added in Mudlet 4.20 (`true` = fresh load,
  `false` = post-`resetProfile()`) to recreate both mapper views, re-subscribe,
  and refresh.
- **Read-only build drift guard.** `--fail-on-diff` now implies `--diff`,
  treats a missing output file as drift, and never invokes the version-bumping,
  archiving build path.
- **Obsolete standalone test removed.** `tests/test_state_validation.py`
  targeted a "State Validator" subsystem that does not exist in the package
  and therefore failed every direct invocation.
- **Package/release version consistency.** `--version` now builds the requested
  version exactly, and default releases adopt the version selected by the
  auto-incrementing build. Packaging refuses an XML/metadata version mismatch.
- **Release preflight ordering.** The clean-tree check now runs before the
  release build creates expected changes; tag, merge, atomic push, and remote
  verification failures now stop the workflow instead of reporting false
  success.
- **Test runner output flags.** `--verbose` now prints runner configuration and
  `--quiet` emits a single status line instead of both flags being no-ops.
- **Test path resolution.** The runner and standalone Python suites now locate
  `LuminariGUI.xml` relative to the repository and work from either root or
  `tests/`.

### Changed

- **Label click callbacks converted to closures.** Replaced the legacy
  string-function-name form (`setClickCallback("demonnicChatSwitch", tab)`)
  with closures in YATCO chat tabs, the tabbed info window, and the
  Legend/Map buttons. The legacy form depends on global name lookup plus
  argument references held in the Lua registry — the surface affected by the
  Mudlet 4.20/4.21 label callback lifetime changes (Mudlet #9254 / #9255).
- **MSDP subscriptions refactored** into `GUI.MSDP_REPORT_VARS` +
  `GUI.requestMSDPReports()`, callable from both the protocol-enabled path and
  the post-reset path. Verified byte-for-byte identical variable coverage
  (33 active variables, unchanged).
- **Removed unsupported stylesheet properties.** Deleted 8 `box-shadow` and 1
  `text-shadow` declarations from Geyser stylesheets. Qt Style Sheets have
  never supported either property; Qt6 parses stylesheets more strictly, where
  an invalid declaration risks the surrounding rule being dropped. (The
  `text-shadow` uses inside `echo()` HTML were left alone — that is Qt's
  rich-text engine, a different parser.)
- **`config.lua` manifest corrected** to match Mudlet's own exporter
  (`src/dlgPackageExporter.cpp`): `dependencies` is now a comma-separated
  string rather than a Lua table, `helpURL` added, and the non-standard
  `modified` field removed.
- **Declared minimum Mudlet raised** from `4.0+` to `4.21+`.

### Documentation

- Added `docs/MUDLET_COMPATIBILITY.md` — Mudlet 4.20–4.22 changes affecting
  this package, known open upstream bugs, and a triage checklist.
- Corrected `docs/MUDLET_DEVELOPMENT.md`, `CONTRIBUTING.md`, and `AGENTS.md`,
  which described an obsolete "single-file architecture" and a deleted
  `scripts/create_package.py`.
- Made `AGENTS.md` canonical and linked `CLAUDE.md` / `GEMINI.md` to it.
- Corrected dependency guidance: omitting `--skip-optional` when a tool such as
  `luacheck` is missing exits 1 before any suite runs.

## [Unreleased] - 2025-11-29

### Added - Package Manager (theGUI/package.py)

- **New Package Manager**: Introduced `theGUI/package.py` for creating distributable packages
  - Cleaner replacement for `scripts/create_package.py` (486 vs 1189 lines)
  - Subcommand-based CLI: `create`, `release`, `list`, `clean`
  - Integrates with build.py and build.yaml for version management
  - Modern Python: pathlib, dataclasses, type hints

- **Package Commands**:
  - `python3 theGUI/package.py create` - Create a local distributable .mpackage (runs build & tests)
  - `python3 theGUI/package.py create --dev` - Create dev package with timestamp
  - `python3 theGUI/package.py release` - Publish refs, GitHub Release page, and both assets
  - `python3 theGUI/package.py release --dry-run` - Preview publication without changes
  - `python3 theGUI/package.py list` - List packages in Releases/
  - `python3 theGUI/package.py clean` - Remove old dev packages

### Removed

- **Deprecated**: Removed `scripts/create_package.py` - replaced by `theGUI/package.py`

### Changed

- Updated `docs/PYTHON_TOOLS.md` with new package.py documentation
- Updated `theGUI/README_theGUI.md` with package manager section
- Updated `CLAUDE.md` with package commands
- Updated `README.md` development section

### Added - Source-to-Build System (theGUI)

- **New Build System**: Introduced `theGUI/` source-to-build system for modular XML development
  - `theGUI/build.py`: Python build script that assembles XML fragments into `LuminariGUI.xml`
  - `theGUI/build.yaml`: Configuration file defining fragment order and build options
  - `theGUI/skeleton.xml`: Template structure for the final assembled XML
  - `theGUI/src/`: Modular XML fragments organized by type:
    - `triggers/`: Trigger definitions (YATCOConfig, GUI)
    - `aliases/`: Alias definitions (Toggles, YATCO)
    - `scripts/`: Script definitions (MSDPMapper, GUI, YATCOConfig, YATCO)
    - `keys/`: Key binding definitions (Movement)

- **Auto-Archiving**: Build system automatically archives previous versions before rebuilding
  - Archives saved to `docs/archive/LuminariGUI.xml_<version>`
  - Preserves version history without manual backup steps
  - Skips archiving if same version already archived

- **Auto-Version Increment**: Build system automatically increments version on each build
  - Increments last part of version (e.g., 2.0.4.016 → 2.0.4.017)
  - Preserves leading zeros in version numbers
  - Updates `build.yaml` with new version automatically
  - Skipped during `--validate` dry-run mode

- **Build Commands**:
  - `python3 theGUI/build.py` - Build the package (increments version, archives old, writes new)
  - `python3 theGUI/build.py --validate` - Validate only, no file changes
  - `python3 theGUI/build.py --extract` - Split existing XML into fragments
  - `python3 theGUI/build.py --diff` - Show what would change
  - `python3 theGUI/build.py --watch` - Rebuild on file changes
  - `python3 theGUI/build.py --stats` - Show fragment statistics

- **New Documentation**:
  - `theGUI/README_theGUI.md`: Complete guide to the source-to-build system
  - `docs/docs-audit.md`: Documentation audit notes
  - `CONTRIBUTING.md`: Contribution guidelines for the project

- **Archive Directory**: `docs/archive/` now stores versioned XML backups
  - `LuminariGUI.xml_2.0.4.015`
  - `LuminariGUI.xml_2.0.4.016`
  - Historical documentation files

### Changed - Project Organization and Infrastructure (2025-11-04)

- **Repository Reorganization**: Complete restructuring of project root for cleaner organization
  - Moved all test files to `tests/` directory:
    - `test_events.py`, `test_functions.py`, `test_lua_quality.py`, `test_lua_syntax.py`
    - `test_performance.py`, `test_state_validation.py`, `test_system.py`
    - `run_tests.py` (test runner)
    - `test_cleanup.lua` (Lua test script)
  - Moved all build/development scripts to `scripts/` directory:
    - `analyze_handlers.py` (resource analysis tool)
    - `create_package.py` (release management)
    - `format_xml.py` (XML formatting utility)
    - `validate_package.py` (XML validation tool)
    - `cleanup_implementation.lua` (reference implementation)
  - Project root now contains only essential files: `LuminariGUI.xml`, `config.lua`, documentation

- **Path Corrections**: Fixed all file references to work from new locations
  - Updated XML file references in test files: `LuminariGUI.xml` → `../LuminariGUI.xml`
  - Updated XML file references in scripts: `LuminariGUI.xml` → `../LuminariGUI.xml`
  - Fixed test import in `validate_package.py`: `test_lua_syntax` → `tests.test_lua_syntax`
  - Updated test config paths: `tests/test_configs/` → `test_configs/` (relative to tests dir)
  - Updated luacheck config file patterns: `tests/sample_scripts/` → `sample_scripts/`

- **Documentation Updates**: Updated all documentation to reflect new structure
  - `CLAUDE.md`: Updated all script command references to use `scripts/` prefix
  - `README.md`: Updated all script and test command references
  - `docs/PYTHON_TOOLS.md`: Updated all tool paths and command examples
  - Fixed markdown links to point to new file locations

- **Changelog Improvements**: Enhanced project history documentation
  - Updated version history table with actual project versions (2.0.4.010 - 2.0.4.016)
  - Created comprehensive historical changelog: `docs/previous_changelogs/2024-01-01_changelog.md`
  - Documented complete project history from March 2020 through July 16, 2025
  - Includes version summaries, contributors list, and technical details

### Technical Details
- All scripts remain fully functional from project root: `python3 scripts/<script>.py`
- All tests work from both root and tests directory: `python3 tests/run_tests.py`
- Zero breaking changes to functionality - only organizational improvements
- Cleaner project root improves navigation and reduces clutter
- Better separation of concerns: source code, tests, scripts, documentation

---
End Changelog entries here
---

## Version History Summary

See [`HISTORICAL_CHANGELOG.md`](HISTORICAL_CHANGELOG.md) for detailed entries
through v2.0.4.016.

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| **2.0.4.017** | 2025-11-29 | Source-to-Build System - New theGUI build system with modular XML fragments, auto-archiving of previous versions, and automatic version increment on each build |
| **2.0.4.016** | 2025-07-31 | Release v2.0.4.016 - Resolved conflicts and cleaned up dev packages |
| **2.0.4.015** | 2025-07-20 | Visual Improvements - Complete UI overhaul with premium gaming aesthetics, enhanced chat colors with channel-specific prefixes, styled containers with dark purple backgrounds and golden borders, improved text display with bold formatting |
| **2.0.4.014** | 2025-07-20 | Numpad Movement Keys - Complete directional movement using numeric keypad + Chat Sound Notifications - Comprehensive sound alert system for all chat channels with `dsound` command, configurable volume control, cooldown system |
| **2.0.4.013** | 2025-07-20 | New "Say" Chat Tab - Dedicated tab for local room communication (say, shout, holler, whisper, ask) + Fixed Mudlet Mapper Room Names - Room names now properly displayed in mapper instead of just VNUMs |
| **2.0.4.012** | 2025-07-18 | Gauge Visual Overhaul - Dramatically improved appearance with gradient colors, golden borders, box shadows, bold fonts with professional labels, text shadows for readability |
| **2.0.4.011** | 2025-07-17 | Icon Tooltips - Added hover tooltips to all icon displays (status effects, action economy) + Fixed Spell-Like Affects Display - Now properly shows spell durations, modifiers, and types |
| **2.0.4.010** | 2025-07-17 | Complete Recovery and Fix Implementation - Restored all features from 2.0.4.007 + Fixed Scrollbar Visibility (light gray handles) and Button System (Legend/Room button nil reference fix) |
