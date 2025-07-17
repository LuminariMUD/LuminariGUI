# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
