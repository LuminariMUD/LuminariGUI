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
- **Validate Package**: `python3 validate_package.py` - Check XML structure, common issues, and Lua syntax
- **Validate XML only**: `python3 validate_package.py --no-lua-syntax` - Skip Lua syntax checking
- **Format XML**: `python3 format_xml.py` - Pretty-print and format the XML file
- **Format with output**: `python3 format_xml.py -o formatted.xml` - Format to new file
- **Format without backup**: `python3 format_xml.py --no-backup` - Skip backup creation

Note: XML validation runs automatically on git commit via pre-commit hook

### Testing Infrastructure
- **Run all tests**: `python3 run_tests.py` - Execute complete test suite
- **Run specific test**: `python3 run_tests.py --test syntax` - Run individual test (syntax, quality, functions, events, system, performance)
- **Parallel execution**: `python3 run_tests.py --parallel` - Run tests in parallel for faster execution
- **Test with report**: `python3 run_tests.py --report results.json --format json` - Generate detailed test report
- **Individual test tools**:
  - `python3 test_lua_syntax.py` - Lua syntax validation using luac
  - `python3 test_lua_quality.py` - Static analysis using luacheck
  - `python3 test_functions.py` - Unit tests for core functions
  - `python3 test_events.py` - Event system testing with mocks
  - `python3 test_system.py` - Memory leak and error boundary testing
  - `python3 test_performance.py` - Performance benchmarks

### Release Management
- **Create release**: `python3 create_package.py --release` - Complete release workflow
- **Release with testing**: `python3 create_package.py --release --run-tests` - Full release with comprehensive testing
- **Development build**: `python3 create_package.py --dev` - Create timestamped dev package
- **Package with tests**: `python3 create_package.py --run-tests` - Create package after running full test suite
- **List packages**: `python3 create_package.py --list` - Show all packages with metadata
- **Dry run**: `python3 create_package.py --release --dry-run` - Test release without changes
- **Git operations**: `python3 create_package.py --git-tag --git-branch --git-commit`
- **Cleanup**: `python3 create_package.py --cleanup-legacy` - Remove old/legacy files
- **Migrate metadata**: `python3 create_package.py --migrate-metadata` - Generate missing JSON files

The release workflow automatically:
1. Validates XML and checks git status
2. Runs comprehensive test suite (if --run-tests specified)
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
2. **Run tests**: `python3 run_tests.py` to catch issues early
3. **Validate changes**: `python3 validate_package.py` for XML and Lua syntax
4. Import into Mudlet to test changes
5. Use Mudlet's error console to debug issues
6. **Pre-commit testing**: Run full test suite before committing
7. Commit changes to git when all tests pass

### Common Tasks

- **Adding a new trigger**: Add a `<Trigger>` element within appropriate `<TriggerGroup>`
- **Adding a new script**: Add a `<Script>` element within `<ScriptPackage>`
- **Modifying chat channels**: Edit triggers in the YATCOConfig group
- **Updating mapper logic**: Modify the MSDPMapper script

### Testing Approach

The project now includes comprehensive automated testing:

#### Automated Testing
1. **Syntax Validation**: `python3 test_lua_syntax.py` - Validates all Lua code syntax
2. **Code Quality**: `python3 test_lua_quality.py` - Static analysis with luacheck
3. **Unit Tests**: `python3 test_functions.py` - Tests core functions with known inputs/outputs
4. **Event Testing**: `python3 test_events.py` - Mocks MSDP events and tests handlers
5. **System Tests**: `python3 test_system.py` - Memory leak and error boundary testing
6. **Performance**: `python3 test_performance.py` - Benchmarks critical functions
7. **Full Suite**: `python3 run_tests.py` - Runs all tests with unified reporting

#### Manual Testing (Still Required)
1. Load the package in Mudlet
2. Connect to LuminariMUD
3. Test functionality manually for user experience
4. Check Mudlet's error console for runtime errors

#### Test Dependencies
- **Required**: `lua` or `luajit` - For running Lua code tests
- **Optional**: `luac` - For syntax validation (syntax tests skipped if missing)
- **Optional**: `luacheck` - For static analysis (quality tests skipped if missing)

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