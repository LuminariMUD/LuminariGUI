# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL WARNING: DO NOT "FIX" THE XML! ⚠️

**THE XML IN THIS PROJECT IS INTENTIONALLY "MALFORMED" AND MUST REMAIN THAT WAY!**

### Why the XML Looks "Broken"
- **Mudlet's XML parser is LENIENT** - it accepts malformed XML that works perfectly
- **Standard XML parsers are STRICT** - they reject this code but it runs fine in Mudlet
- **The code WORKS** in its intended environment (Mudlet client)

### Specific "Issues" That Are ACTUALLY CORRECT:
1. **Misspelled elements**: `<conditonLineDelta>` (not `<conditionLineDelta>`) - **REQUIRED by Mudlet**
2. **Self-closing tags**: `<regexCodeList />` (with space) - **REQUIRED format**
3. **Unescaped characters in strings**: `"<gray>Hello"` - **WORKS in Mudlet context**
4. **XML entities in some places**: `&lt;white&gt;` - **REQUIRED for some display code**

### AI Behavior Warning
**AI assistants will try to "fix" these issues** because they look like errors. **DO NOT LET THEM!**
- Fixing the XML spelling breaks Mudlet compatibility
- Fixing the color tags breaks UI display
- Fixing the self-closing tags breaks package loading

### What This Means for Development
- **The code works perfectly** in Mudlet
- **Tests will fail** because they use standard XML parsers
- **Only 3 tests pass**: `test_functions.py`, `test_events.py`, `test_performance.py`
- **5 tests fail**: All XML-parsing dependent tests
- **This is intentional and acceptable**

## Project Overview

LuminariGUI is a Mudlet GUI package for LuminariMUD, a text-based MUD game. The entire codebase is contained within a single XML file (`LuminariGUI.xml`) that includes Lua scripts, triggers, and aliases embedded in Mudlet's package format.

## Development Commands

### Package Management
- **Load Package**: Import `LuminariGUI.xml` into Mudlet client
- **Test Changes**: Reload the package in Mudlet after modifications
- **Debug**: Use Mudlet's built-in Lua console and error viewer

### XML Validation & Formatting
- **Validate Package**: `python3 validate_package.py` - Check XML structure, common issues, and Lua syntax
- **Validate XML only**: `python3 validate_package.py --no-lua-syntax` - Skip Lua syntax checking
- **Format XML**: `python3 format_xml.py` - Pretty-print and format the XML file
- **Format with output**: `python3 format_xml.py -o formatted.xml` - Format to new file
- **Format without backup**: `python3 format_xml.py --no-backup` - Skip backup creation

**⚠️ IMPORTANT**: These tools will report "errors" that are actually correct for Mudlet. This is expected and acceptable. The XML is designed for Mudlet's parser, not standard XML validators.

Note: XML validation runs automatically on git commit via pre-commit hook

### Testing Infrastructure

**⚠️ TESTING LIMITATIONS**: Due to Mudlet-specific XML format, only 3 tests work with current XML:
- ✅ **PASS**: `python3 test_functions.py` - Unit tests for core functions
- ✅ **PASS**: `python3 test_events.py` - Event system testing with mocks  
- ✅ **PASS**: `python3 test_performance.py` - Performance benchmarks
- ❌ **FAIL**: `python3 test_lua_syntax.py` - Cannot parse Mudlet XML
- ❌ **FAIL**: `python3 test_lua_quality.py` - Cannot parse Mudlet XML
- ❌ **FAIL**: `python3 test_system.py` - Cannot parse Mudlet XML
- ❌ **FAIL**: `python3 validate_package.py` - Cannot parse Mudlet XML
- ❌ **FAIL**: `python3 format_xml.py` - Cannot parse Mudlet XML

**This is expected and acceptable** - the XML works perfectly in Mudlet.

#### Available Test Commands
- **Run working tests**: `python3 run_tests.py --test functions events performance`
- **Run all tests**: `python3 run_tests.py` - Shows 3 pass, 5 fail (expected)
- **Individual working tests**:
  - `python3 test_functions.py` - Unit tests for core functions
  - `python3 test_events.py` - Event system testing with mocks
  - `python3 test_performance.py` - Performance benchmarks

### Release Management
- **Create release**: `python3 create_package.py --release --skip-validation` - Complete release workflow
- **Development build**: `python3 create_package.py --dev --skip-validation` - Create timestamped dev package
- **List packages**: `python3 create_package.py --list` - Show all packages with metadata
- **Dry run**: `python3 create_package.py --release --dry-run --skip-validation` - Test release without changes
- **Git operations**: `python3 create_package.py --git-tag --git-branch --git-commit`
- **Cleanup**: `python3 create_package.py --cleanup-legacy` - Remove old/legacy files
- **Migrate metadata**: `python3 create_package.py --migrate-metadata` - Generate missing JSON files

**⚠️ IMPORTANT**: Always use `--skip-validation` flag because the XML validation will fail on Mudlet-specific formatting.

The release workflow automatically:
1. ~~Validates XML and checks git status~~ (SKIP - use --skip-validation)
2. ~~Runs comprehensive test suite~~ (SKIP - only 3 tests work)
3. Updates version in XML headers and CHANGELOG.md
4. Creates release branch and commits changes
5. Creates package with metadata
6. Creates git tag
7. Optionally pushes to remote (with --push flag)

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

1. **⚠️ CRITICAL: XML Escaping Rules Are Complex**:
   - **Color tags in strings**: `"<gray>Hello"` - **LEAVE AS-IS** (works in Mudlet)
   - **XML-like patterns**: `"&lt;/WILDERNESS_MAP&gt;"` - **MUST stay escaped**
   - **Comparison operators**: `if x &lt; y then` - **MUST stay escaped**
   - **HTML in display**: `"&lt;center&gt;Text&lt;/center&gt;"` - **MUST stay escaped**
   - **DO NOT apply blanket escaping rules** - each case is contextual

2. **Mudlet-Specific Requirements**:
   - `<conditonLineDelta>` - **MUST stay misspelled** (Mudlet expects this)
   - `<regexCodeList />` - **MUST have space** before closing slash
   - Self-closing tags vary by context - **DO NOT standardize**

3. **Event System**: The package uses Mudlet events extensively:
   - Custom events are raised with `raiseEvent()`
   - Event handlers are registered with `registerAnonymousEventHandler()`

4. **MSDP Protocol**: Server communication uses MSDP for data exchange:
   - Room information for mapping
   - Character stats and status
   - Game state updates

5. **Image Assets**: Status effect icons and UI elements are in `images/` directory:
   - `affected_by/` - Status effect icons (60+ PNG files)
   - `buttons/`, `frame/` - UI graphics

### Development Workflow

1. Edit the `LuminariGUI.xml` file directly
2. **Run working tests**: `python3 run_tests.py --test functions events performance`
3. **Create test package**: `python3 create_package.py --dev --skip-validation`
4. **Import into Mudlet** to test changes (THIS IS THE REAL TEST)
5. **Use Mudlet's error console** to debug issues
6. **Manual testing**: Test actual functionality in game
7. **Commit changes** when functionality works in Mudlet

**⚠️ IMPORTANT**: Skip XML validation tools - they will report false errors. The only valid test is whether it works in Mudlet.

### Common Tasks

- **Adding a new trigger**: Add a `<Trigger>` element within appropriate `<TriggerGroup>`
- **Adding a new script**: Add a `<Script>` element within `<ScriptPackage>`
- **Modifying chat channels**: Edit triggers in the YATCOConfig group
- **Updating mapper logic**: Modify the MSDPMapper script

### Troubleshooting Commands

- **Fix GUI refresh issues**: `fix gui` - Comprehensive fix for all GUI elements
  - Re-registers all event handlers (Group tab, gauges, Player tab, ASCII map)
  - Re-initializes chat system if needed
  - Manually refreshes all displays with current MSDP data
  - Reports exactly which components were refreshed
- **Fix chat positioning**: `fix chat` - Repositions chat window if it appears in wrong location
- **Toggle group display**: `show self` - Shows/hides yourself in the Group tab
- **Toggle chat gagging**: `gag chat` - Enables/disables chat message gagging

### Testing Approach

#### Automated Testing (Limited)
Due to Mudlet-specific XML formatting, only 3 automated tests work:
1. **Unit Tests**: `python3 test_functions.py` - Tests core functions with known inputs/outputs ✅
2. **Event Testing**: `python3 test_events.py` - Mocks MSDP events and tests handlers ✅  
3. **Performance**: `python3 test_performance.py` - Benchmarks critical functions ✅

#### Manual Testing (PRIMARY METHOD)
**This is the main testing approach for this project:**
1. **Load the package in Mudlet** - The ultimate test
2. **Connect to LuminariMUD** - Test with real game data
3. **Test functionality manually** - User experience testing
4. **Check Mudlet's error console** - Runtime error detection
5. **Test specific features**:
   - Chat gag toggles (`gag chat`)
   - Group display toggles (`show self`)
   - Map display and triggers
   - Status effect icons
   - UI responsiveness

#### Test Dependencies
- **Required**: `lua` or `luajit` - For running the 3 working tests
- **Optional**: `luac` - For syntax validation (not usable due to XML issues)
- **Optional**: `luacheck` - For static analysis (not usable due to XML issues)

## Dependencies

### Runtime Dependencies
- Mudlet client (runtime environment)
- LuminariMUD server (for manual testing)
- No external Lua libraries (all functionality uses Mudlet's built-in APIs)

### Development Dependencies
- Python 3.6+ (for testing infrastructure and build tools)
- `lua` or `luajit` (required for automated testing)
- `luac` (optional, for syntax validation)
- `luacheck` (optional, for static code analysis)