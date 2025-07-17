# Changelog

All notable changes to this project will be documented in this file.

**IMPORTANT**: When releasing a new version, update the version number in:
1. This CHANGELOG.md file (add new version entry)
2. LuminariGUI.xml (line 3: `<MudletPackage version="X.X.X">`)
3. *Only on release versions: README.md (update download links and version references)

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.4.007] - 2025-07-17

### Released
- Production release after testing and verification
- All features from 2.0.4.006 confirmed working as expected

## [2.0.4.006] - 2025-07-17

### Added
- **Horizontal Scroll Toggle**: New `hscroll` command for main window
  - Toggles between word wrap (default) and horizontal scrolling modes
  - When enabled: Disables word wrap, shows horizontal scrollbar for long lines
  - When disabled: Returns to normal word wrapping at ~100 characters
  - Setting persists across sessions via `GUI.toggles.lua`
  - Requires Mudlet 4.10+ for full functionality

### Changed
- **Container Layout Adjustments**: Optimized right-side container proportions
  - Action Icons container: Increased height from 8% to 11% (37.5% more space)
  - Action Icons container: Moved up from y=92% to y=89%
  - Room Info container: Reduced height from 42% to 39%
  - Better visual balance for action economy display

### Technical Details
- Added version checking for `enableHorizontalScrollBar` compatibility
- Horizontal scrollbar uses existing dark theme styling from v2.0.4.005
- Main window scrolling behavior independent of GUI components

## [2.0.4.005] - 2025-07-17

### Fixed
- **Container Content Sizing**: Fixed content appearing too large in adjustable containers
  - All content now properly accounts for title bar (~25px) and container padding (9px)
  - Updated positioning for: Status Gauges, Button Panel, Room Info, Tabbed Info Window, Action Icons, ASCII Map
  - Standardized positioning pattern: `x=9, y=25, width="-18", height="-34"`

- **Chat Container**: Fixed YATCO chat content overflow using wrapper container approach
  - Created inner container (`GUI.chatContainerInner`) with proper offsets
  - YATCO now builds inside the wrapper, respecting title bar and padding
  - Maintains full YATCO functionality without modifying library code

- **Action Icons Alignment**: Fixed icons appearing too low in container
  - Added `vertical-align: top` CSS property to align icons to top of HBox
  - Icons now properly positioned without excessive gap below title bar

- **Horizontal Scrollbar**: Added missing horizontal scrollbar styling
  - Previously invisible due to lack of custom styling
  - Now matches vertical scrollbar appearance (dark theme)
  - Same background (#202020) and border (#515151) colors

- **Fix GUI Command**: Added defensive check to prevent error on first install
  - Shows helpful message instead of Lua error if GUI not fully loaded
  - Instructs users to reload profile if needed

### Technical Details
- Container content positioning now consistently accounts for Adjustable Container structure
- Wrapper container pattern used for third-party components (YATCO)
- CSS vertical alignment used for icon positioning without structural changes
- Complete scrollbar styling for both orientations

## [2.0.4.004] - 2025-07-17

### Fixed
- **Container Content Sizing**: Initial attempt to fix content sizing in adjustable containers
  - Note: This version had incomplete fixes, see 2.0.4.005 for complete solution

## [2.0.4.003] - 2025-07-17

### Fixed
- **Enhanced `fix gui` Command**: Now restores ALL adjustable containers when used
  - Previously only restored 5 containers (Status Gauges, Character Stats, Action Icons, Chat, Mudlet Map)
  - Now also restores: Button Panel, Room Info Container, Cast Console, and ASCII Map Container
  - All 9 containers can be recovered after accidentally closing them
  - Room info data is refreshed when the container is restored
  - ASCII Map container visibility is properly handled based on current map mode

### Technical Details
- Added explicit `:show()` and `:raise()` calls for missing containers in `GUI.initializeOrRefresh()`
- Maintains proper z-order and visibility states for all containers
- ASCII Map container is always created but visibility controlled by ASCII/Mudlet toggle

## [2.0.4.002] - 2025-07-17

### Changed
- **Adjustable Containers**: Added `noClose = true` parameter to prevent accidental container closure
  - Added to default container style configuration
  - Applied to all 9 container creation calls
  - Note: This parameter may not actually remove close buttons in current Mudlet version
  - Users can still minimize and lock containers

### Technical Details
- Modified `GUI.AdjustableContainers.defaultStyle` to include `noClose = true`
- Updated all container creation calls to explicitly include the parameter
- No functional changes to container behavior aside from close button attempt

## [2.0.4.001] - 2025-07-16

### Fixed
- **MSDP System Restoration**: Complete fix for MSDP event handling and GUI initialization
  - Fixed critical GUI initialization crash by removing non-existent `addToProfile()` function calls
  - Fixed sysProtocolEnabled event handler registration timing with early registration
  - Added missing MSDP variable REPORT requests (PSP, PSP_MAX, ROOM data)
  - Added GUI refresh trigger when MSDP protocol is enabled
  - All MSDP-driven UI elements now properly update: health/PSP/movement gauges, group tab, player stats
  - Fixed event handlers being registered as function references instead of strings
  - GUI.init() now completes successfully, allowing all systems to function

- **UI Visual Fixes**: Restored proper appearance to GUI components
  - Fixed Player tab missing background texture (stylesheet overwrite issue)
  - Fixed Cast Console MiniConsole overlapping the container title bar
  - All tabbed info panels now display consistent styling and backgrounds

### Summary
This release stabilizes the entire MSDP and GUI system after the Adjustable Container migration. All major GUI components now function correctly with proper event handling, visual styling, and user interaction.

## [2.0.3.005] - 2025-07-16

### Fixed
- **Player Tab Background**: Fixed missing background texture in Player tab
  - The init_player() function was overwriting the entire stylesheet, removing background and texture
  - Now properly preserves background color, texture image, and font while adding alignment
  - Player tab now matches the appearance of Affects and Group tabs

- **Cast Console Title Bar**: Fixed MiniConsole overlapping the container title
  - MiniConsole was positioned at (0,0) covering the "Cast Console" title text
  - Now positioned at y=25 to start below title bar, with proper padding offsets
  - Title bar is now fully visible and console content properly contained

## [2.0.3.004] - 2025-07-16

### Fixed
- **MSDP Protocol Initialization**: Fixed sysProtocolEnabled event handler registration timing
  - Added early registration of protocol handler to catch MSDP enablement
  - Added missing MSDP variable REPORT requests (PSP, PSP_MAX, ROOM data)  
  - Added GUI refresh trigger when MSDP protocol is enabled
  - This ensures all GUI components properly initialize when connecting to the MUD

- **Critical GUI Initialization Crash**: Removed non-existent `addToProfile()` function calls
  - Removed calls from Cast Console and ASCII Map initialization
  - These calls were causing GUI.init() to crash, preventing event handler registration
  - This was the root cause of MSDP updates not working after the initial fix

## [2.0.3.001] - 2025-07-16

### Fixed
- **CRITICAL**: Fixed MSDP event handler registration
  - Root cause: Event handlers were being registered as function references instead of strings
  - Fixed `GUI.registerEventHandlers()` to use string handler names (e.g., "GUI.updateGroup" instead of GUI.updateGroup)
  - This is the MINIMAL fix that resolves all MSDP issues without breaking anything else
  - All MSDP-driven UI elements now properly update: health/PSP/movement gauges, group tab, player stats, etc.

## [2.0.2] - 2025-07-15

### Added
- **Adjustable Container Foundation**: Complete infrastructure for user-customizable GUI
  - Created GUI.AdjustableContainers namespace with full container management
  - Implemented container registration and lifecycle management
  - Added profile system (default, combat, social, minimal)
  - Configured auto-save/load with custom directory structure
  - Established consistent naming conventions (LuminariGUI_[ComponentName])

### Changed
- **Tabbed Info Window**: Converted to Adjustable.Container for user customization
  - Migrated GUI.tabbedInfoWindow from static Geyser container to Adjustable.Container
  - Created new container "LuminariGUI_TabbedInfo" with full adjustable capabilities
  - Maintains backward compatibility with existing code through GUI.Box4 reference
  - Preserves all tab functionality (Player, Affects, Group tabs)
  - Maintains MSDP event handling for automatic updates
  - Container can now be resized, repositioned, minimized, and settings persist across sessions
  - Added to default layout profile with top-left screen attachment

- **Room Information**: Converted to Adjustable.Container for user customization
  - Migrated GUI.Box5 from static Geyser label to Adjustable.Container
  - Created new container "LuminariGUI_RoomInfo" with full adjustable capabilities
  - Maintains backward compatibility with existing code through GUI.Box5 reference
  - Preserves room info display and map legend functionality
  - Maintains MSDP event handling for room updates (msdp.ROOM)
  - Container can now be resized, repositioned, minimized, and settings persist across sessions
  - Added to default layout profile with top-right screen attachment
  - Phase 2 of Adjustable Container migration now complete (4 of 4 core components)

- **Button Panel**: Converted to Adjustable.Container for user customization
  - Migrated GUI.Box3 from static Geyser label to Adjustable.Container
  - Created new container "LuminariGUI_ButtonPanel" with full adjustable capabilities
  - Maintains backward compatibility with existing code through GUI.Box3 reference
  - Preserves all button functionality (Legend toggle, Mudlet/ASCII map switching)
  - Button styling and responsiveness maintained
  - Container can now be resized, repositioned, minimized, and settings persist across sessions
  - Added to default layout profile with top-right screen attachment
  - First component of Phase 3 (Secondary Migration) completed

- **Action Icons**: Converted to Adjustable.Container for user customization
  - Migrated GUI.ActionIconsBox from embedded VBox in Status to standalone Adjustable.Container
  - Created new container "LuminariGUI_ActionIcons" with full adjustable capabilities
  - Maintains backward compatibility with existing code through GUI.ActionIconsBox reference
  - Preserves all action icon functionality (Standard, Move, Swift actions)
  - Maintains MSDP event handling for action state updates (msdp.ACTIONS)
  - Icons correctly display active/inactive states with appropriate images
  - Container can now be resized, repositioned, minimized, and settings persist across sessions
  - Added to default layout profile with top-right screen attachment
  - Second component of Phase 3 (Secondary Migration) completed

- **Map**: Converted to Adjustable.Container to resolve z-order issues
  - Migrated map.container from static Geyser.Container to Adjustable.Container
  - Created new container "LuminariGUI_Map" with full adjustable capabilities
  - Preserves all map functionality (Geyser.Mapper, minimap switching)
  - Fixes z-order issues where Controls container was trapped behind map
  - Container can now be resized, repositioned, minimized like other components
  - Added proper z-order management to ensure containers layer correctly
  - Map is kept at back layer with other containers raised above it

- **Cast Console**: Converted to Adjustable.Container for user customization
  - Migrated GUI.castConsole from embedded MiniConsole in GUI.Box2 to Adjustable.Container
  - Created new container "LuminariGUI_CastConsole" with full adjustable capabilities
  - Maintains backward compatibility with existing code through GUI.castConsole reference
  - Preserves all spell casting functionality (start, complete, abort, cancel)
  - Maintains spell name display and casting status messages
  - Console auto-clears after 10 seconds following cast completion/failure
  - Container can now be resized, repositioned, minimized, and settings persist across sessions
  - Added to default layout profile with bottom-left screen attachment
  - Phase 3 of Adjustable Container migration now complete (3 of 3 secondary components)
  - **IMPORTANT**: This separation also fixed the Chat container which was previously conflicting!

- **Chat System**: Now working as Adjustable.Container (Fixed by Cast Console separation)
  - GUI.chatContainer was already created but wasn't functioning due to conflicts
  - Separating Cast Console into its own container resolved the initialization issue
  - Chat system now has full adjustable capabilities (resize, reposition, minimize)
  - All chat channels working (Tell, Congrats, Chat, Auction, Group, Wiz)
  - Tab blinking and gagging functionality preserved
  - Chat history and timestamps maintained
  - ALL 8 MAIN COMPONENTS NOW MIGRATED - 100% Complete!

### Fixed
- **ASCII Map Display**: Fixed critical bug where ASCII map wasn't visible
  - Created separate `GUI.asciiMapContainer` as Adjustable Container
  - Moved `map.minimap` from nested static container to independent Adjustable Container
  - Updated button callbacks (`asciiClick`/`mudletClick`) to properly show/hide containers
  - Fixed all references in triggers (Capture Wilderness Map, Capture Room Map)
  - Updated environment switching logic for Wilderness/Room transitions
  - Added proper z-order management with `raise()` to ensure visibility
  - ASCII map now properly toggles with Mudlet map via Controls buttons
  - Added to default profile for layout persistence

- **UI Layout Reorganization**: Complete 3-column layout implementation
  - Column 1 (50%): Main window (0%, 0%, 50%, 60%) and Chat (0%, 60%, 50%, 30%)
  - Column 2 (25%): Controls (50%, 0%), Tabbed Info (50%, 20%), Cast Console (50%, 60%), Status (50%, 75%)
  - Column 3 (25%): Map/ASCII Map (75%, 0%, 25%, 50%), Room Info (75%, 50%, 25%, 34%), Action Icons (75%, 84%, 8%, 8%)
  - Fixed all container positioning to exact specifications
  - Removed old static UI remnants (GUI.Box2 background sections)

- **Initialization System**: Updated for Adjustable Container system
  - Fixed `fix gui` command to properly handle all adjustable containers
  - Fixed `fix chat` command (changed from `fixchat`) to prevent full-screen issue
  - Removed problematic resize("100%", "100%") calls that caused chat to take entire screen
  - Added mode checking for map container to show correct map type (ASCII vs Mudlet)
  - Ensures all containers display correctly after reconnection or package reload

### Removed
- **Frame Images**: Removed all incompatible frame image references
  - Removed 14 frame image files from images/frame/ directory
  - Frame images were incompatible with Adjustable Container system
  - Cleaned up all code references to frame images

## [2.0.2] - 2025-07-15

### Fixed
- **CRITICAL**: Fixed background texture rendering issue that caused light/white appearance instead of dark concrete texture
  - Root cause: Code referenced `ui_texture.png` but actual file was `ui_texture.jpg`
  - Fixed file extension mismatch in both `GUI.BoxCSS` and tabbed window CSS generation
  - This resolves the fundamental container rendering problem where neither texture nor dark purple fallback was visible
  - Expected result: Dark gray concrete texture background should now render properly in GUI sections
- **CRITICAL**: Fixed Group tab and other GUI elements not auto-refreshing after package reload
  - Root cause: Event handlers sometimes fail to register properly during package initialization
  - Added robust `GUI.registerEventHandlers()` function with error handling and verification
  - Added automatic verification and refresh of all GUI components after 2-second delay
  - Enhanced `fix gui` command to comprehensively refresh all GUI elements
  - Now automatically refreshes: Group tab, health/movement/experience gauges, Player tab, room info, and ASCII map
  - Added proper enemy gauge handling: only shows during combat, hides when not in combat
  - This resolves the issue where Group tab, health gauges, and other MSDP-driven elements stop updating automatically
- **CRITICAL**: Fixed chat system not initializing when package imported mid-session
  - Root cause: `demonnicOnInstall` only checked for "YATCO" package name, not "LuminariGUI"
  - Fixed package detection to check for both "YATCO" and "LuminariGUI" package names
  - Added chat system verification and auto-initialization to `GUI.registerEventHandlers()`
  - Added chat system re-initialization to `fix gui` command with error handling
  - This resolves the issue where chat tabs don't work when importing package during active session
- Fixed auction channel capture by updating regex patterns to match actual game verbs
  - Changed `auctions` to `auctalks` for incoming auction messages
  - Changed `auction` to `auctalk` for outgoing auction messages
  - This resolves the issue where auction channel messages were not being captured in the chat system

### Added
- Completed comprehensive analysis of left-side GUI structure and components
  - Documented complete container hierarchy (GUI.Left → GUI.Box4/Box7 → tabbed interface)
  - Analyzed 9-piece border frame system using medieval-style PNG images
  - Mapped Player/Affects/Group tab system structure and relationships
  - Identified status gauge layout (health, experience, movement, opponent info)
  - Documented critical dependencies (Geyser framework, CSSMan, MSDP protocol)
  - Added detailed 6-layer background rendering analysis with expected visual results
  - Documented rendering order from base purple background through texture overlays to final components
  - Mapped key image assets (ui_texture.png, frame PNG files, button.png)
