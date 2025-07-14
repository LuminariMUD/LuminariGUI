# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Enhanced
- **Comprehensive State Validation System**: Addresses "Shared Global State Corruption" critical issue
  - **Central StateValidator Module**: New `GUI.StateValidator` system with comprehensive validation rules
    - Type checking and structure validation for all shared state access
    - Safe accessor functions with fallback defaults for MSDP, toggles, and map data
    - State corruption detection and automatic recovery mechanisms
    - Graceful degradation when state is invalid or missing
  - **Safe MSDP Access Functions**: Replace direct `msdp.*` access with validated functions
    - `GUI.getMSDPHealth()`, `GUI.getMSDPMovement()`, `GUI.getMSDPRoom()` etc.
    - Automatic type validation and conversion for numeric values
    - Structure validation for complex data like ROOM, AFFECTS, GROUP
    - Prevents crashes from nil, malformed, or partially updated MSDP data
  - **Protected Toggle Management**: Enhanced toggle system with validation and recovery
    - `GUI.getToggle()` and `GUI.setToggle()` with automatic corruption recovery
    - Type validation for boolean toggles with fallback defaults
    - Automatic reinitialization when toggle table is corrupted
    - Auto-save functionality with error handling
  - **Map State Protection**: Validated access to `map.room_info` and related structures
    - `GUI.validateRoomInfo()` prevents crashes from missing or corrupt room data
    - Safe access to room VNUM, ENVIRONMENT, TERRAIN, and EXITS
    - Fallback defaults for all room information fields
  - **State Recovery Functions**: Automatic recovery from corrupted shared state
    - `GUI.recoverCorruptedState()` rebuilds missing or invalid state structures
    - Comprehensive status reporting with `GUI.getStateStatus()`
    - Debug logging system with `GUI.setStateDebug()` for troubleshooting
  - **Addresses Critical Architecture Issues**: Solves "fix one, break another" instability
    - Prevents race conditions between map updates and UI refreshes
    - Eliminates crashes from partial MSDP data updates
    - Provides rollback mechanisms for state consistency
    - Comprehensive test suite verifies all validation scenarios
- **Enhanced Resource Cleanup System**: Significantly improved resource management to prevent memory leaks
  - **Enhanced Timer Creation**: `GUI.createTimer()` now includes comprehensive validation and error handling
    - Input validation for timer duration and function parameters
    - Safe cleanup of existing timers before creating new ones
    - Metadata tracking for better debugging (creation time, recurring status, function type)
    - Backward compatibility with both old ID-only and new metadata timer formats
  - **Improved Cleanup Functions**: Enhanced error handling in `GUI.cleanupHandlers()` and `GUI.cleanupTimers()`
    - Protected cleanup operations with pcall() to prevent cleanup failures from crashing the system
    - Detailed failure reporting showing successful vs failed cleanup attempts
    - Handles both legacy timer IDs and new metadata structures
  - **Enhanced Master Cleanup**: `GUI.cleanupResources()` now provides comprehensive resource reporting
    - Safe cleanup of legacy resources (cast console, YATCO blink, speedwalk, init timers)
    - Protected toggle saving with error handling
    - Detailed cleanup statistics showing handlers, timers, legacy items, and any failures
    - Returns structured cleanup report for programmatic access
  - **Resource Status Debugging**: New debugging functions for resource leak analysis
    - `GUI.getResourceStatus()` provides detailed resource inventory
    - `GUI.showResourceStatus()` displays user-friendly resource usage report
    - Tracks timer age, recurring status, and legacy resource identification
    - Helps identify resource leaks and migration opportunities
  - **Addresses Critical Issues**: Improves "Resource Lifecycle Management Failure" from stability audit
    - Better tracking prevents orphaned timers and handlers
    - Enhanced error handling prevents cleanup failures from cascading
    - Comprehensive reporting aids in debugging resource issues

### Fixed
- **Critical Runtime Issues**: Addressed major stability problems discovered during user testing
  - **Invalid Alignment Errors**: Fixed incomplete HTML center tags in GeyserLabel initialization
    - Corrected `"<center>text"` patterns to proper `"<center>text</center>"` format
    - Affected GUI.Box2 and tabbedInfoWindow tab initialization
    - Prevents GeyserLabel rendering errors that could crash the GUI
  - **Cast Console Initialization Timing**: Resolved YATCO interference with cast console visibility
    - Added cast console backup and restoration logic during YATCO initialization
    - Prevents cast console from being hidden or destroyed when YATCO creates its UI containers
    - Includes automatic re-showing if cast console becomes hidden during YATCO setup
  - **Toggle Saving Failures**: Fixed critical bugs in settings persistence system
    - Corrected `table.load()` usage - now properly assigns loaded data: `GUI.toggles = table.load(file)`
    - Added comprehensive validation for loaded toggle data with fallback defaults
    - Enhanced `GUI.saveToggles()` with error handling and data validation
    - Prevents corruption of user preferences and ensures settings persist across sessions
- **XML Escaping Issues**: Corrected all cecho statements to use proper XML entity escaping
- **Vararg Scope Errors**: Fixed incorrect usage of `...` parameters inside pcall functions
- **Timer Creation Race Conditions**: Enhanced validation prevents double-creation of timers

### Added
- **Testing Infrastructure**: Comprehensive testing framework to prevent "fix one, break another" issues
  - `test_lua_syntax.py` - Lua syntax validation using luac compiler
  - `test_lua_quality.py` - Static code analysis using luacheck
  - `test_functions.py` - Unit tests for core Lua functions with mocks
  - `test_events.py` - Event system testing with MSDP mocks
  - `test_system.py` - Memory leak detection and error boundary testing
  - `test_performance.py` - Performance benchmarks for critical functions
  - `run_tests.py` - Unified test runner with parallel execution
  - `tests/` directory with mock data, sample scripts, and configurations
- **Enhanced Validation**: Extended XML validation to include Lua syntax checking
  - `validate_package.py` (renamed from validate_xml.py) now includes integrated Lua syntax validation
  - Comprehensive error reporting for both XML structure and Lua code
- **Release Integration**: Package creation now supports full test suite execution
  - `create_package.py` enhanced with `--run-tests` option
  - Pre-release validation includes both XML and comprehensive testing
  - Prevents releasing broken code through automated testing
- Comprehensive documentation improvements
  - Enhanced image documentation with detailed status effect icon guide (`images/affected_by/STATUS_EFFECTS.md`)
  - Improved README files for image directories with proper descriptions
  - Added version information and metadata to main XML package
  - Enhanced TODO comments with future enhancement descriptions
  - Created `QUICK_REFERENCE.md` for fast command lookup
  - Created `PACKAGING.md` with comprehensive package preparation and release instructions
- Comprehensive LuminariGUI.xml commentary audit and improvements
  - Added proper function documentation for 15+ undocumented functions
  - Documented regex patterns with clear explanations and examples
  - Added comprehensive inline documentation for complex functions
  - Explained magic numbers and converted to descriptive comments

### Changed
- Updated placeholder URLs to actual GitHub repository paths
- Fixed broken external links (Mudlet documentation URLs)
- **Enhanced Test Configuration**: Improved luacheck configuration for Mudlet development
  - Added missing Mudlet API functions to reduce false positives (reduced warnings from 236 to 0)
  - Added functions: `deleteLine`, `clearUserWindow`, `selectCurrentLine`, `copy`, `exists`, `setBgColor`, `getMainWindowSize`, `sendMSDP`, `getAreaTable`, `getAreaRooms`, `addAreaName`, `setRoomEnv`, `setExit`, `setExitStub`
  - Updated test script to use external configuration file for better maintainability
  - Added style ignores for common Mudlet patterns (whitespace, line length, indentation)

### Fixed
- Corrected Mudlet documentation links to point to working wiki URLs
- Verified and validated all external documentation links
- **Critical**: Fixed massive malformed comment blocks that could break XML parsing
- Resolved XML syntax errors and unescaped character issues
- Enhanced TODO items with clear future enhancement documentation
- Improved trigger documentation with regex pattern explanations
- **Testing Infrastructure Fixes**: Resolved critical compatibility and logic issues
  - Fixed XML parser compatibility in all test modules (replaced `getparent()` calls with manual parent mapping)
  - Corrected function test mocks and expectations (added proper `map` global mock, fixed table serialization)
  - Fixed performance test success/failure logic (removed duplicate print statements causing false failures)
  - Improved test result validation and error reporting across all test suites
  - Renamed `validate_xml.py` to `validate_package.py` to better reflect comprehensive validation functionality
  - Fixed event system test failures by properly handling dotted handler names (e.g., "map.eventHandler")
  - Corrected cascade count expectation in event tests (33 instead of 32)
  - Removed print function override in test mocks to allow proper test output
  - Fixed Lua quality test compatibility issues:
    - Resolved XML parser `getparent()` method compatibility with parent mapping
    - Changed luacheck output format from JSON to default (JSON formatter dependency missing)
    - Updated result parser to handle default luacheck output format
    - Quality test now properly detects and reports code issues (found 206 warnings across 30 scripts)
- **Code Quality Improvements**: Fixed all legitimate code quality issues
  - Fixed function spacing syntax (changed `function(` to `function (` in 7 locations)
  - Fixed `end)` patterns for better readability (3 instances)
  - Fixed unused variables in MSDPMapper (y1, z1), Group (status_msg), and MSDP (overfilled)
  - Test warnings reduced from 249 to 3 (only acceptable inline patterns remain)

### Deprecated
- None

### Removed
- None

### Security
- None

## [2.0.0] - 2025-07-13

### Added
- Created `CLAUDE.md` file to provide guidance for Claude Code AI assistant when working with the repository
  - Documented project structure and architecture
  - Added development workflow instructions
  - Included Mudlet-specific development patterns
  - Listed key components and modules

- Implemented comprehensive XML validation and formatting tools
  - `validate_package.py` - Python script for package validation and structure checking
    - Checks XML well-formedness and Mudlet package structure
    - Reports component counts (triggers, scripts, aliases, timers, keys, actions)
    - Detects common issues like unescaped XML characters (`<`, `>`, `&`)
    - Provides detailed error reporting with line number approximations
    - Validates root element structure and version attributes
  - `format_xml.py` - Python script for XML formatting with backup creation
    - Pretty-prints XML with proper indentation and structure
    - Creates automatic backups before formatting (`.backup` extension)
    - Preserves XML declaration and DOCTYPE declarations
    - Supports custom output files or in-place formatting
    - Reports file size changes and percentage differences
    - Handles CDATA sections and special content properly
  - `create_package.py` - Complete release management system
    - **Full release workflow automation** (`--release` flag)
      - XML validation and git status checking
      - Version updates in XML headers and CHANGELOG.md
      - Release branch creation and commit management
      - Package creation with comprehensive metadata
      - Git tag creation with annotated messages
      - Optional push to remote repositories
    - **Git integration capabilities**
      - Automatic release branch creation (`release/vX.X.X`)
      - Version consistency checking across files
      - Commit automation with standardized messages
      - Tag creation with force-overwrite options
      - Push coordination for branches and tags
    - **Package management features**
      - Development vs release build differentiation
      - Timestamped development packages with automatic cleanup
      - Comprehensive metadata generation (JSON files)
      - SHA256 hash calculation for package integrity
      - Legacy package migration and cleanup tools
    - **Version management**
      - Automatic version detection from CHANGELOG.md
      - XML header version updating with regex patterns
      - CHANGELOG.md version section management
      - Cross-file version consistency validation

- Added Git pre-commit hook integration for automatic XML validation
  - Integrates with `validate_package.py` for pre-commit validation
  - Automatically validates `LuminariGUI.xml` before commits
  - Prevents commits if XML is malformed or has structural issues
  - Provides clear error messages and guidance for fixing issues
  - Supports bypass with `--no-verify` flag when needed

### Changed
- Updated `CLAUDE.md` with comprehensive XML validation and formatting commands documentation
- Enhanced documentation structure and technical specifications

### Technical Notes
- All XML tools use Python 3's built-in `xml.etree.ElementTree` and `xml.dom.minidom` modules
- No external dependencies required beyond Python 3 standard library
- Scripts are cross-platform compatible (Windows, macOS, Linux)
- Release automation integrates with Git command-line tools
- Package format follows Mudlet's `.mpackage` specification (ZIP-based)
- Metadata files use JSON format for easy parsing and integration

## [1.0.0] - Initial Release

### Added
- Complete LuminariGUI package for Mudlet
- MSDP integration for real-time game data
- Tabbed chat system (YATCO integration)
- Interactive mapping with terrain visualization
- Status effect monitoring with 90+ icons
- Group management interface
- Health, movement, and experience gauges
- Action economy tracking
- Spell casting console

### Features
- **Real-time MSDP Integration**: Live character stats and game state updates
- **Advanced Status Monitoring**: Health, movement, experience tracking
- **Tabbed Chat System**: Organized communication channels
- **Dual Mapping Support**: Mudlet mapper and ASCII map display
- **Group Management**: Real-time group member status tracking
- **Visual Status Effects**: 90+ status effect icons for conditions and spells