# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation improvements
  - Enhanced image documentation with detailed status effect icon guide (`images/affected_by/STATUS_EFFECTS.md`)
  - Improved README files for image directories with proper descriptions
  - Added version information and metadata to main XML package
  - Enhanced TODO comments with future enhancement descriptions
  - Created `QUICK_REFERENCE.md` for fast command lookup
- Comprehensive LuminariGUI.xml commentary audit and improvements
  - Added proper function documentation for 15+ undocumented functions
  - Documented regex patterns with clear explanations and examples
  - Added comprehensive inline documentation for complex functions
  - Explained magic numbers and converted to descriptive comments

### Changed
- Updated placeholder URLs to actual GitHub repository paths
- Fixed broken external links (Mudlet documentation URLs)
- Expanded CHANGELOG.md with proper version history and release structure

### Fixed
- Corrected Mudlet documentation links to point to working wiki URLs
- Verified and validated all external documentation links
- **Critical**: Fixed massive malformed comment blocks that could break XML parsing
- Resolved XML syntax errors and unescaped character issues
- Enhanced TODO items with clear future enhancement documentation
- Improved trigger documentation with regex pattern explanations

## [2.0.0] - Development Tools & Documentation

### Added
- Created `CLAUDE.md` file to provide guidance for Claude Code AI assistant when working with the repository
  - Documented project structure and architecture
  - Added development workflow instructions
  - Included Mudlet-specific development patterns
  - Listed key components and modules

- Implemented XML validation and formatting tools
  - `validate_xml.py` - Python script for XML validation
    - Checks XML well-formedness
    - Validates Mudlet package structure
    - Reports component counts (triggers, scripts, aliases, etc.)
    - Detects common issues like unescaped XML characters
  - `format_xml.py` - Python script for XML formatting
    - Pretty-prints XML with proper indentation
    - Creates automatic backups before formatting
    - Preserves XML declaration and DOCTYPE
    - Supports custom output files
    - Reports file size changes

- Added Git pre-commit hook for automatic XML validation
  - Located in `.git/hooks/pre-commit`
  - Automatically validates `LuminariGUI.xml` before commits
  - Prevents commits if XML is malformed
  - Provides clear error messages

### Changed
- Updated `CLAUDE.md` with XML validation and formatting commands documentation

### Technical Notes
- All XML tools use Python 3's built-in `xml.etree.ElementTree` module
- No external dependencies required
- Scripts are cross-platform compatible

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