# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LuminariGUI is a Mudlet GUI package for LuminariMUD, a text-based MUD game. The entire codebase is contained within a single XML file (`LuminariGUI.xml`) that includes Lua scripts, triggers, and aliases embedded in Mudlet's package format.

## Development Commands

### Package Management
- **Load Package**: Import `LuminariGUI.xml` into Mudlet client
- **Test Changes**: Reload the package in Mudlet after modifications
- **Debug**: Use Mudlet's built-in Lua console and error viewer

### XML Validation & Formatting
- **Validate XML**: `python3 validate_xml.py` - Check XML structure and common issues
- **Format XML**: `python3 format_xml.py` - Pretty-print and format the XML file
- **Format with output**: `python3 format_xml.py -o formatted.xml` - Format to new file
- **Format without backup**: `python3 format_xml.py --no-backup` - Skip backup creation

Note: XML validation runs automatically on git commit via pre-commit hook

## Architecture & Code Structure

### Main Components

1. **LuminariGUI.xml** (3532 lines) - Single package file containing:
   - **Triggers**: Pattern matchers for game text (chat channels, combat, status updates)
   - **Scripts**: Core functionality modules
   - **Aliases**: User command shortcuts

### Key Scripts & Modules

- **MSDPMapper**: Handles MSDP protocol communication for automatic room mapping
- **GUI Framework**: Uses Geyser (Mudlet's UI framework) for layout management
- **Chat System**: Implements tabbed chat using demonnic's framework
- **CSSMan**: CSS styling manager for UI components

### Code Organization Pattern

Within the XML, code is structured as:
```xml
<Script>
  <name>ScriptName</name>
  <script>-- Lua code here</script>
</Script>
```

### Important Considerations

1. **XML Escaping**: When editing Lua code within XML, special characters must be escaped:
   - `<` becomes `&lt;`
   - `>` becomes `&gt;`
   - `&` becomes `&amp;`

2. **Event System**: The package uses Mudlet events extensively:
   - Custom events are raised with `raiseEvent()`
   - Event handlers are registered with `registerAnonymousEventHandler()`

3. **MSDP Protocol**: Server communication uses MSDP for data exchange:
   - Room information for mapping
   - Character stats and status
   - Game state updates

4. **Image Assets**: Status effect icons and UI elements are in `images/` directory:
   - `affected_by/` - Status effect icons (60+ PNG files)
   - `buttons/`, `frame/` - UI graphics

### Development Workflow

1. Edit the `LuminariGUI.xml` file directly
2. Import into Mudlet to test changes
3. Use Mudlet's error console to debug issues
4. Commit changes to git when working properly

### Common Tasks

- **Adding a new trigger**: Add a `<Trigger>` element within appropriate `<TriggerGroup>`
- **Adding a new script**: Add a `<Script>` element within `<ScriptPackage>`
- **Modifying chat channels**: Edit triggers in the YATCOConfig group
- **Updating mapper logic**: Modify the MSDPMapper script

### Testing Approach

Since there's no automated testing framework:
1. Load the package in Mudlet
2. Connect to LuminariMUD
3. Test functionality manually
4. Check Mudlet's error console for Lua errors

## Dependencies

- Mudlet client (runtime environment)
- LuminariMUD server (for testing)
- No external Lua libraries (all functionality uses Mudlet's built-in APIs)