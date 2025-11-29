# LuminariGUI Images

This directory contains all image assets used by the LuminariGUI package:

## Directory Structure
- **affected_by/** - Status effect icons (90 PNG files)
- **buttons/** - UI button graphics and controls
- **frame/** - UI frame elements and borders
- **Various files** - Background textures, UI elements, and decorative graphics

## Image Categories
- **Status Effects**: Visual indicators for character conditions and spell effects
- **UI Components**: Buttons, frames, and interface elements
- **Decorative Elements**: Background images and aesthetic enhancements

## Testing & Validation

Image assets are validated as part of the automated testing infrastructure:
- **Asset validation**: Tests verify all referenced images exist
- **Path testing**: Cross-platform path handling is tested
- **Performance testing**: Image loading performance is benchmarked

For detailed information about status effect icons, see `affected_by/STATUS_EFFECTS.md`.

## Development Notes

When adding new images:
1. Follow existing naming conventions
2. Optimize file sizes for performance
3. Update any hardcoded references in test files
4. Run `python3 run_tests.py` to ensure no tests are broken
