# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
