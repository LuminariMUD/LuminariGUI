# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Previous Changelogs: `docs/previous_changelogs/`

---
Begin Changelog entries below
---

## [Unreleased] - 2025-11-29

### Added - Package Manager (theGUI/package.py)

- **New Package Manager**: Introduced `theGUI/package.py` for creating distributable packages
  - Cleaner replacement for `scripts/create_package.py` (486 vs 1189 lines)
  - Subcommand-based CLI: `create`, `release`, `list`, `clean`
  - Integrates with build.py and build.yaml for version management
  - Modern Python: pathlib, dataclasses, type hints

- **Package Commands**:
  - `python3 theGUI/package.py create` - Create release .mpackage (runs build & tests)
  - `python3 theGUI/package.py create --dev` - Create dev package with timestamp
  - `python3 theGUI/package.py release` - Full workflow (build, test, branch, package, tag)
  - `python3 theGUI/package.py release --dry-run` - Preview release without changes
  - `python3 theGUI/package.py release --push` - Release and push to remote
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
  - `docs/ongoing_projects/source-to-build.md`: Project planning documentation
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

See Previous Changelogs for More Details: `docs/previous_changelogs/`

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
