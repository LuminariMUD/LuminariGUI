# Changelog - Historical Archive (2020-2025)

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Note**: This file contains the historical changelog entries from project inception through July 16, 2025 (prior to v2.0.4.001).

---

## [2.0.4.001] - 2025-07-16

### In Development
- **Adjustable Containers System**: Beginning implementation of user-adjustable GUI components
  - Research phase for adjustable window framework
  - Initial work on container positioning and resizing
  - Foundation for customizable GUI layout system

---

## [2.0.2] - 2025-07-15

### Added
- **Event Handler Recovery System**: New `fix gui` command for comprehensive GUI refresh
  - Re-registers all event handlers (Group tab, gauges, Player tab, ASCII map)
  - Re-initializes chat system if needed
  - Manually refreshes all displays with current MSDP data
  - Reports exactly which components were refreshed

### Fixed
- **Critical Background Texture Rendering**: Resolved texture loading issues
  - Fixed UI texture path and loading mechanism
  - Ensured proper texture display across all containers
- **Documentation Updates**: Updated README.md with current feature set and commands

### Changed
- Cleaned up development packages from repository
- Improved stability and error recovery mechanisms

---

## [2.0.0] - 2025-07-14

### Major Release - Testing Infrastructure and Resource Management

### Added
- **Comprehensive Testing Framework**: Complete testing infrastructure to prevent regressions
  - `test_lua_syntax.py` - Lua syntax validation using luac compiler
  - `test_lua_quality.py` - Static code analysis using luacheck
  - `test_functions.py` - Unit tests for core Lua functions with mocks
  - `test_events.py` - Event system testing with MSDP mocks
  - `test_system.py` - Memory leak detection and error boundary testing
  - `test_performance.py` - Performance benchmarks for critical functions
  - `run_tests.py` - Unified test runner with parallel execution
  - `tests/` directory with mock data, sample scripts, and configurations

- **Resource Cleanup System**: Comprehensive resource management to prevent memory leaks
  - New `Resource Cleanup` script for centralized tracking of event handlers and timers
  - Helper functions `GUI.registerHandler()` and `GUI.createTimer()` for automatic resource tracking
  - Automatic cleanup on `sysUninstall` and `sysExitEvent` to prevent memory leaks
  - Migration function for existing handlers to use new tracking system
  - Modified scripts to use tracked resources: Config (33 handlers), MSDPMapper (6 handlers), Cast Console (3 timers), Toggles (2 handlers)

- **Enhanced Package Creation**: Improved build and release tools
  - `create_package.py` - Automated package creation with version management
  - `validate_package.py` - Comprehensive XML and Lua syntax validation
  - `format_xml.py` - XML formatting and pretty-printing utility
  - Integration with test suite via `--run-tests` option
  - Prevents releasing broken code through automated validation

- **Comprehensive Logging System**: Structured error handling and debugging
  - Centralized logging with debug categories
  - `debug`, `debug list`, `debugc <category>` commands for runtime debugging
  - PII-safe logging for production use

- **Documentation Improvements**: Enhanced project documentation
  - `CLAUDE.md` - AI assistant guidance for development
  - `QUICK_REFERENCE.md` - Fast command lookup reference
  - `PACKAGING.md` - Package preparation and release instructions
  - Enhanced image documentation with status effect icon guide
  - Improved README files with proper descriptions
  - Added version information and metadata to main XML package

### Changed
- **Code Quality Improvements**: Fixed all legitimate code quality issues
  - Fixed function spacing syntax (7 locations)
  - Fixed unused variables in MSDPMapper, Group, and MSDP handlers
  - Test warnings reduced from 249 to 3 (only acceptable patterns remain)

- **Enhanced Test Configuration**: Improved luacheck configuration
  - Added missing Mudlet API functions (reduced false positives from 236 to 0)
  - Updated test scripts to use external configuration files
  - Added style ignores for common Mudlet patterns

### Fixed
- **Critical XML Issues**: Fixed massive malformed comment blocks that could break XML parsing
- **Testing Infrastructure Fixes**: Resolved compatibility and logic issues
  - Fixed XML parser compatibility across all test modules
  - Corrected function test mocks and expectations
  - Fixed performance test success/failure logic
  - Improved test result validation and error reporting
  - Fixed event system test failures with dotted handler names

- **Documentation**: Corrected broken external links and placeholder URLs
  - Updated Mudlet documentation links to working wiki URLs
  - Verified and validated all external documentation links

### Technical Details
- Added comprehensive inline documentation for complex functions
- Explained magic numbers with descriptive comments
- Documented regex patterns with clear explanations and examples
- Added proper function documentation for 15+ undocumented functions

---

## [1.x] - 2020-2025 (Historical Releases)

### [1.4] - 2020-05-04
**Community Contributions by rrebrick**

#### Added
- **Smarter Speedwalk**: Improved speedwalking functionality with general client module improvements
  - Enhanced pathfinding and movement automation
  - Better error handling for speedwalk commands

#### Fixed
- **Experience to Level Calculation**: Fixed experience needed to level calculation
  - Corrected formula for experience requirements
  - Improved display accuracy in status gauges

---

### [1.3] - 2020-04-26
**Community Contributions by rrebrick**

#### Changed
- General XML improvements and bug fixes
- Enhanced client stability and performance

---

### [1.2] - 2020-04-26
**Community Contributions by rrebrick**

#### Changed
- Initial community contributions merged
- Various improvements to core functionality

---

### [1.1] - 2020-03-15
**Documentation and Images**

#### Added
- Comprehensive image asset library
  - Status effect icons (60+ PNG files in `images/affected_by/`)
  - UI button graphics
  - Border frame graphics (9-piece system)
  - Background textures
- README documentation for image directories
- Initial project documentation

---

### [1.0] - 2020-03-15
**Initial Release**

#### Added
- **Core GUI Framework**: Complete Mudlet GUI package for LuminariMUD
  - Geyser-based layout management
  - Tabbed information windows (Player, Affects, Group)
  - Room information display with legend
  - Chat system integration

- **MSDP Integration**: Full MSDP protocol support
  - Room information for auto-mapping
  - Character stats tracking (HP, PSP, Movement)
  - Combat data display
  - Group information
  - Status effects monitoring
  - Game state updates

- **Mudlet Mapper Integration**: Automatic room mapping
  - MSDP-driven room creation
  - Exit tracking and display
  - Room name and VNUM display
  - Area navigation support

- **Status Displays**: Real-time character information
  - Health, PSP, and Movement gauges
  - Enemy health tracking
  - Experience progress display
  - Status effect icons in header
  - Action economy indicators

- **Chat System**: Multi-channel chat management
  - Tabbed interface for different channels
  - Channel-specific message routing
  - Chat gagging toggle (`gag chat`)
  - Tab organization for easy navigation

- **ASCII Map Display**: In-game ASCII map rendering
  - Server-sent map display
  - Synchronized with player position
  - Configurable display area

- **Button Controls**: Quick access GUI buttons
  - Legend toggle
  - Mudlet mapper toggle
  - ASCII map toggle

- **User Commands**: Chat and display management
  - `gag chat` - Toggle chat message gagging
  - `show self` - Toggle self display in Group tab
  - Various debug commands for development

- **Visual Styling**: Professional UI appearance
  - CSS-based theming system (CSSMan)
  - Consistent color schemes
  - Responsive layout design
  - Custom fonts and styling

#### Technical Features
- **Event System**: Comprehensive event handling
  - MSDP variable change handlers
  - System event handlers (connect, disconnect, load, exit)
  - Custom event support with `raiseEvent()`

- **Settings Persistence**: User preferences saved across sessions
  - Toggle states stored in `GUI.toggles.lua`
  - Chat preferences
  - Display settings
  - Window positions and sizes

- **Resource Management**: Proper cleanup and initialization
  - Event handler registration and cleanup
  - Timer management
  - Proper uninstall handling

---

## Version Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 2.0.4.001 | 2025-07-16 | Development: Adjustable containers system |
| 2.0.2 | 2025-07-15 | Event handler recovery, background texture fix |
| 2.0.0 | 2025-07-14 | Testing infrastructure, resource cleanup system, comprehensive logging |
| 1.4 | 2020-05-04 | Smarter speedwalk, experience calculation fix |
| 1.3 | 2020-04-26 | Community contributions and improvements |
| 1.2 | 2020-04-26 | Initial community contributions |
| 1.1 | 2020-03-15 | Documentation and image assets |
| 1.0 | 2020-03-15 | Initial release with core functionality |

---

## Contributors

- **Zusuk** - Original author and maintainer
- **rrebrick** - Community contributions (speedwalk improvements, experience fixes)
- **LuminariMUD Development Team** - Testing and feedback

---

## Notes

- This changelog covers the period from initial release (March 2020) through July 16, 2025
- For changes after July 16, 2025, see the main CHANGELOG.md file
- Version 2.0.4.001 and later have detailed changelog entries in their respective version-specific files
- The project uses semantic versioning (MAJOR.MINOR.PATCH.BUILD)
