# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
