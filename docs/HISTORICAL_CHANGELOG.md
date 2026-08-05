# Historical Changelog (2020-2025)

This document consolidates the two historical changelog snapshots that were
previously stored in `docs/previous_changelogs/`. Both snapshots entered the
repository in commit `3327d5c`; their release entries and source ordering are
retained below so version provenance remains visible in the working tree and
in Git history.

## Snapshot: project inception through July 16, 2025

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Source file**: `docs/previous_changelogs/2024-01-01_changelog.md`

**Coverage**: Project inception through July 16, 2025, including v2.0.4.001.

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

---

## Snapshot: July 17-31, 2025

**Source file**: `docs/previous_changelogs/2025-07-31_changelog.md`

The source snapshot contained an empty `Unreleased` section. It is omitted
here because it carried no release history.

## [2.0.4.016] - 2025-07-31

No detailed entry was recorded in the source snapshot.

## [2.0.4.015] - 2025-07-20

### Changed
- **Visual Improvements**: Complete UI overhaul with premium gaming aesthetics
  - Enhanced chat colors with channel-specific prefixes ([GSAY], [OOC], [TELL], etc.)
  - Styled containers with dark purple backgrounds (rgba(38, 25, 47, 0.9)) and golden borders
  - Improved text display with bold formatting and better color coding
  - Added hover and pressed effects to buttons with golden glow
  - Enhanced status displays in Player, Group, and Room info tabs
  - Added shadows and improved contrast throughout the interface
  - Fixed Mudlet color tag compatibility (silver -> light_gray)
  - Improved attribute column spacing in Player tab
  - Increased tab header height to prevent button cutoff

## [2.0.4.014] - 2025-07-20

### Added
- **Numpad Movement Keys**: Complete directional movement using the numeric keypad
  - Numpad 1: Southwest
  - Numpad 2: South
  - Numpad 3: Southeast
  - Numpad 4: West
  - Numpad 5: Look
  - Numpad 6: East
  - Numpad 7: Northwest
  - Numpad 8: North
  - Numpad 9: Northeast
  - Numpad /: Inventory
  - Numpad *: Scan
  - Numpad -: Up
  - Numpad +: Down

- **Chat Sound Notifications**: Comprehensive sound alert system for chat messages
  - New `dsound` command to quickly toggle chat sounds on/off
  - Plays notification sound (audio/chat_sound.mp3) for ALL chat channels when enabled
  - Sound alerts work on all tabs including the "All" tab
  - Configurable volume control (0-100)
  - Cooldown system to prevent sound spam
  - Settings persist across sessions via GUI.toggles system

### Features
- **Sound Management Commands**:
  - `dsound` - Quick toggle for chat sounds (with test sound on enable)
  - `set chat sound on/off` - Enable or disable sounds permanently
  - `set chat sound volume <0-100>` - Adjust notification volume
  - `set chat sound file <filename>` - Use custom sound file
  - `set chat sound cooldown <seconds>` - Set minimum time between sounds
  - `set chat sound test` - Test current sound configuration

- **Smart Sound Behavior**:
  - Sounds play for messages on ANY chat channel when enabled
  - No sound when viewing the specific channel where message arrives
  - Works correctly on "All" tab (plays for all incoming messages)
  - Multiple fallback options: package sound -> user directory -> system beep
  - Sound file path follows same pattern as images: `getMudletHomeDir()/LuminariGUI/audio/`

### Fixed
- **Critical All Tab Bug**: Fixed early return in blink logic that prevented sounds on "All" tab
  - Removed `return` statement that was exiting append() function prematurely
  - Sound notifications now work correctly regardless of which tab is active

### Technical Implementation
- Sound configuration added to YATCO config with sensible defaults
- Modified `demonnic.chat:append()` function to include sound playback logic
- Integrated with existing GUI.toggles persistence system
- Added audio directory to package creation script
- Included chat_sound.mp3 (46,570 bytes) as default notification sound
- Fixed multiple `playSound()` calls that aren't available in Mudlet (replaced with `playSoundFile()`)

### Package Updates
- Updated create_package.py to include audio/ directory in packages
- Audio files are now properly packaged and extracted to LuminariGUI directory

## [2.0.4.013] - 2025-07-20

### Added
- **New "Say" Chat Tab**: Created a dedicated tab for local room communication
  - Captures all say, shout, and holler messages
  - Includes whisper messages (both to and from player)
  - Includes ask messages (both to and from player)
  - Messages are automatically routed to both the Say tab and the All tab
  - Respects chat gagging settings when enabled

### Fixed
- **Mudlet Mapper Room Names**: Room names are now properly displayed in the mapper
  - Added `setRoomName()` call in the `make_room()` function
  - Mapper now shows actual room names instead of just VNUMs
  - Room names are pulled from MSDP data (`msdp.ROOM.NAME`)

## [2.0.4.012] - 2025-07-18

### Enhanced
- **Gauge Visual Overhaul**: Dramatically improved the appearance of all status gauges
  - Updated color schemes:
    - Health gauge: Gradient red (#8B0000 background to #FF6B6B foreground)
    - Movement gauge: Gradient gold (#B8860B background to #FFD700 foreground)
    - Experience gauge: Gradient purple (#4B0082 background to #9370DB foreground)
    - Enemy gauge: Gradient purple (#4B0082 background to #9370DB foreground)
  - Enhanced gauge styling:
    - Golden borders (#B8731B) with 2px width for premium appearance
    - Box shadows with inset depth and outer glow effects
    - Increased border radius to 10px for smoother corners
    - Semi-transparent backgrounds (rgba(0,0,0,0.3)) on empty gauge areas
  - Improved text display:
    - Bold fonts with larger sizes (14-16px base, current values emphasized)
    - Professional labels: "HEALTH", "MOVES", "EXP" instead of generic names
    - Dynamic text sizing: current values (16px) larger than max values (14px)
    - Black text with white shadow on gold/purple gauges for maximum visibility
    - Text shadows (1px 1px 2px) for better readability
  - Overall achieved a premium gaming UI appearance with depth and polish

### Fixed
- **Text Visibility**: Fixed text color issues on Movement and Health gauges
  - All gauge text now consistently uses black color with white shadow for visibility
  - Ensures readability across all gauge color schemes

### Technical Notes
- Modified `GUI.GaugeBackCSS` and `GUI.GaugeFrontCSS` with enhanced styling properties
- Updated all gauge echo functions to use consistent text formatting
- Maintained compatibility with existing gauge update mechanisms

## [2.0.4.011] - 2025-07-17

### Added
- **Icon Tooltips**: Added hover tooltips to all icon displays
  - Status effect icons in the header now show effect names
  - Status effect icons in the gauge container show effect names
  - Action economy icons show "Standard Action", "Move Action", and "Swift Action"
  - All tooltips display for 10 seconds on hover

### Fixed
- **Spell-Like Affects Display**: Fixed bug where spell-like affects weren't being displayed in the Affects tab
  - Added missing call to `GUI.updateSLAffects()` in the update cycle
  - Now properly shows spell durations, modifiers, and types
- **Tooltip Readability**: Implemented proper CSS technique to ensure all tooltips have clean white backgrounds
  - Used QLabel selector to prevent border-image inheritance to tooltips
  - Ensures tooltip text is always readable against white background

### Technical Changes
- Modified icon CSS implementation to use direct `setStyleSheet()` with QLabel selectors
- Removed incorrect CSSMan usage that was incompatible with selector syntax

## [2.0.4.010] - 2025-07-17

### Complete Recovery and Fix Implementation

This release completes the recovery from the 2.0.4.008 regression incident where the codebase was inadvertently reverted to version 2.0.2. This version includes all features from 2.0.4.007 plus the originally intended fixes from 2.0.4.008.

### Fixed
- **Scrollbar Visibility**: Successfully re-implemented the scrollbar improvements
  - Scrollbar handles now use light gray (#d0d0d0) for better visibility
  - Scrollbar borders use light gray (#a0a0a0) for improved contrast
  - Arrow indicators changed to dark gray (#404040) to be visible on light handles
  - Affects all scrollbars throughout Mudlet (main window and all GUI components)

- **Button System**: Fixed the Legend/Room button issue
  - Reverted button array from "Legend/Room" back to "Legend" to fix nil reference errors
  - This prevents the "attempt to index field 'Legendbutton' (a nil value)" error
  - All control buttons (Legend, Mudlet, ASCII) now function properly

### Included Features
All features from version 2.0.4.007 remain intact:
- Adjustable Container system (all 9 GUI components)
- MSDP event handling and auto-refresh functionality
- Chat system initialization and tab functionality
- Horizontal scrolling toggle feature (`hscroll` command)
- All container layout optimizations
- All bug fixes from versions 2.0.3.001 through 2.0.4.007

### Technical Summary
- Based on commit b05636b (v2.0.4.007) as the stable foundation
- Re-applied the scrollbar and button fixes that were lost during the 2.0.4.008 incident
- Package creation script improvements from 2.0.4.008 are retained
- This is the recommended production version for all users

## [2.0.4.009] - 2025-07-17

### Critical Recovery Release

This release addresses a critical regression that occurred during the 2.0.4.008 release process, where the codebase was inadvertently reverted to version 2.0.2, resulting in the loss of all features and fixes from versions 2.0.3.001 through 2.0.4.007.

### Fixed
- **Codebase Recovery**: Restored all features from version 2.0.4.007
  - Adjustable Container system (all 9 GUI components)
  - MSDP event handling and auto-refresh functionality
  - Chat system initialization and tab functionality
  - Horizontal scrolling toggle feature
  - All container layout optimizations
  - All bug fixes from versions 2.0.3.001 through 2.0.4.007

### Known Issues
- Scrollbar visibility improvements from 2.0.4.008 need to be re-implemented
- Button system fix for "Legend/Room" from 2.0.4.008 needs to be re-implemented
- Package creation script improvements from 2.0.4.008 are retained

### Technical Notes
- This release is based on commit b05636b (v2.0.4.007) with changelog updates
- Future releases will re-implement the intended 2.0.4.008 fixes on the correct codebase
- All users should upgrade directly to this version to restore full functionality

## [2.0.4.008] - 2025-07-17

### Fixed
- **Scrollbar Visibility**: Changed scrollbar colors to light theme for better visibility
  - Scrollbar handles now use light gray (#d0d0d0) instead of dark gray
  - Scrollbar borders now use light gray (#a0a0a0) for better contrast
  - Arrow indicators changed to dark gray (#404040) to be visible on light handles
  - Affects all scrollbars throughout Mudlet (main window and all GUI components)

- **Button System**: Fixed critical button creation failure caused by forward slash in button name
  - Reverted button array from "Legend/Room" back to "Legend" to fix nil reference errors
  - Button now displays "Legend/Room" text while maintaining proper variable naming
  - Fixed button text persistence - "Legend/Room" now shows correctly in both toggle states
  - All control buttons (Legend/Room, Mudlet, ASCII) now function properly again

- **Package Creation Script**: Fixed critical version detection bug in create_package.py
  - Script was defaulting to ancient version 2.0.0 when auto-detection failed
  - Version regex only supported 3-part versions (X.Y.Z), not 4-part (X.Y.Z.NNN)
  - Now supports both version formats and reads from XML file as fallback
  - Removed all hardcoded default versions - script now requires explicit version
  - Prevents silent creation of incorrectly versioned packages

### Technical Details
- Button system requires exact naming match between array values and callback references
- Forward slashes in button names create invalid Lua variable names
- Scrollbar styling uses Qt stylesheets applied at profile level
- Package script checks CHANGELOG.md first, then XML file for version detection
