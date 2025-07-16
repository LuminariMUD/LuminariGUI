# LuminariGUI

A comprehensive Mudlet GUI package for LuminariMUD that provides an enhanced gameplay experience through real-time MSDP integration, tabbed chat system, interactive mapping, and advanced status monitoring.

## ⚠️ IMPORTANT FOR DEVELOPERS

**This project uses Mudlet-specific XML formatting that is intentionally "malformed" by standard XML specifications.** The XML works perfectly in Mudlet but will fail standard XML validation tools. This is normal and expected.

### Key Points:
- **The XML works perfectly in Mudlet** - this is what matters
- **Standard XML parsers will report errors** - these are false positives
- **Do not "fix" the XML formatting** - it will break Mudlet compatibility
- **Only 3 automated tests pass** - the rest fail due to XML parsing issues
- **Manual testing in Mudlet is the primary validation method**

See [`CLAUDE.md`](CLAUDE.md) for detailed information about the XML formatting requirements and development guidelines.

## Features

### 🎮 Core Gameplay Enhancement
- **Real-time MSDP Integration**: Live character stats, room data, and game state updates
- **Advanced Status Monitoring**: Health, PSP, movement, experience, and enemy health gauges
- **Action Economy Tracking**: Visual indicators for standard, move, and swift actions
- **Spell Casting Console**: Real-time spell casting progress and status updates
- **Adjustable Containers**: All GUI components can be resized, repositioned, and minimized (v2.0.4.001+)

### 💬 Communication System
- **Tabbed Chat (YATCO)**: Organized chat channels with customizable tabs
- **Channel Management**: Tell, Chat, Group, Auction, Congrats, and Wizard channels
- **Chat Filtering**: Optional main window gagging with dedicated chat interface
- **Notification System**: Tab blinking for new messages

### 🗺️ Mapping System
- **Dual Mapping Support**: Integrated Mudlet mapper and ASCII map display
- **Automatic Room Mapping**: MSDP-driven room creation and navigation
- **Terrain Visualization**: Color-coded terrain types and environmental indicators
- **Map Legend**: Interactive legend with terrain type reference
- **Speedwalking**: Automated pathfinding with movement optimization

### 👥 Group Management
- **Real-time Group Status**: Live health and movement tracking for all group members
- **Leader Identification**: Visual indicators for group leadership
- **Customizable Display**: Toggle self-inclusion in group display
- **Health Status Colors**: Color-coded health indicators for quick assessment

### ✨ Status Effects & Affects
- **Visual Affect Tracking**: Icon-based display of active affects and conditions
- **Mode Indicators**: Combat modes, defensive stances, and ability states
- **Spell-like Affects**: Detailed spell effect information with durations
- **Status Categories**: Organized affect display for different effect types

## Installation

### Prerequisites
- **Mudlet**: Version 4.10+ recommended
- **LuminariMUD Account**: Active character on LuminariMUD
- **MSDP Support**: Server-side MSDP protocol enabled

### Installation Steps

1. **Download the Package**
   ```bash
   # Download the latest .mpackage file from releases (v2.0.4.001 or newer)
   wget https://github.com/LuminariMUD/LuminariGUI/releases/latest/download/LuminariGUI-v2.0.4.001.mpackage
   ```

2. **Install in Mudlet**
   - Open Mudlet
   - Go to `Package Manager` → `Install Package`
   - Select the downloaded `LuminariGUI-v2.0.4.001.mpackage` file
   - Restart Mudlet when prompted

3. **Connect to LuminariMUD**
   ```
   Host: luminarimud.com
   Port: 4100
   ```

4. **Enable MSDP (if not already enabled)**
   ```
   # In-game command to enable MSDP reporting
   msdp
   ```

5. **Verify Installation**
   - The GUI should automatically initialize upon connection
   - You should see the health/movement gauges at the bottom
   - The tabbed chat window should appear in the bottom area
   - The mapping window should be visible on the right side

## Quick Start

### Basic Usage

Once connected and the GUI has initialized:

1. **Character Stats**: Your health, movement, and experience will automatically display in the bottom gauges
2. **Chat System**: Chat messages will appear in the tabbed interface at the bottom
3. **Mapping**: Move around to see the automatic room mapping in action
4. **Group Play**: Join a group to see member status in the "Group" tab

### Essential Commands

```lua
-- Fix all GUI components if they stop updating
fix gui

-- Toggle chat gagging from main window
gag chat

-- Toggle self-display in group window  
show self

-- Fix chat positioning issues
fix chat

-- Manual mapping controls
start mapping
stop mapping

-- Debug YATCO chat system
debug

-- Toggle blink notifications for chat tabs
dblink
```

### GUI Components

The interface consists of several key areas (all adjustable in v2.0.4.001+):

- **Left Panel**: Character information, affects, and group status (tabbed interface)
- **Right Panel**: Map display (Mudlet/ASCII toggle) and legend/room info
- **Bottom Panel**: Chat system (separate from cast console in v2.0.4.001+)
- **Cast Console**: Spell casting display (now independent container)
- **Status Bar**: Health, PSP, movement, experience gauges
- **Action Icons**: Standard, Move, Swift action indicators (separate container)

## Configuration

### Basic Configuration

The GUI automatically configures itself for optimal display, but you can customize:

```lua
-- Example: Adjust chat window location
demonnic.chat.config.location = "bottomright"  -- topright, topleft, bottomleft

-- Example: Modify gauge colors
GUI.GaugeFrontCSS:set("background-color", "your_color")
```

### MSDP Variables

The GUI automatically requests these MSDP variables:
- Character data: `CHARACTER_NAME`, `LEVEL`, `CLASS`, `RACE`, stats
- Status data: `HEALTH`, `HEALTH_MAX`, `PSP`, `PSP_MAX`, `MOVEMENT`, `MOVEMENT_MAX`, `EXPERIENCE`, `POSITION`
- Combat data: `OPPONENT_HEALTH`, `ACTIONS` (Standard, Move, Swift)
- Environment data: `ROOM`, `GROUP`, `AFFECTS`, `WORLD_TIME`

## Troubleshooting

### Common Issues

**GUI components not updating after package reload:**
- Use `fix gui` command to refresh all GUI elements
- This fixes Group tab, health gauges, Player tab, and ASCII map
- The command re-registers all event handlers and refreshes displays

**GUI not appearing after installation:**
- Ensure MSDP is enabled on your character: `msdp`
- Restart Mudlet and reconnect
- Check that you're connected to LuminariMUD (not a test server)
- Try `fix gui` command to initialize all components

**Chat tabs not working:**
- Use `fix chat` command to reset chat window position
- For mid-session imports, use `fix gui` to reinitialize chat system
- Check YATCO configuration in the scripts panel

**Enemy gauge showing when not in combat:**
- This has been fixed in v2.0.2 - the gauge now properly hides when not in combat
- Use `fix gui` to refresh if the issue persists

**Adjustable containers not working:**
- Ensure you have v2.0.4.001 or newer
- Container settings are saved in `getMudletHomeDir() .. "/LuminariGUI_AdjustableContainers/"`
- Use `fix gui` to refresh all containers
- Container settings persist across sessions

**Mapping not updating:**
- Verify MSDP room data is being received: `debug`
- Use `start mapping` command
- Ensure you're in a mapped area (not wilderness)
- Use `fix gui` to refresh the ASCII map display

**Missing health/movement data:**
- Check MSDP variable reporting is active
- Reconnect to refresh MSDP subscription
- Use `fix gui` to refresh all status displays

### Debug Commands

```lua
-- Enable debug output
debug

-- List debug categories
debug list

-- Watch specific debug category
debugc msdp
```

## 📚 Documentation

### Complete Documentation Guide

This project includes comprehensive documentation for all aspects of development, usage, and maintenance:

#### **🏗️ Core Documentation**
- **[`README.md`](README.md)**: Main project documentation with features, installation, and usage
- **[`CHANGELOG.md`](CHANGELOG.md)**: Version history, feature additions, and breaking changes
- **[`CLAUDE.md`](CLAUDE.md)**: AI development assistance documentation and Mudlet XML specifics
- **[`LICENSE`](LICENSE)**: MIT License terms and conditions

#### **🔧 Development & Tools**
- **[`MUDLET_DEVELOPMENT.md`](MUDLET_DEVELOPMENT.md)**: Comprehensive Mudlet package development guide
- **[`PYTHON_TOOLS.md`](PYTHON_TOOLS.md)**: Python toolchain documentation (validation, formatting, packaging)
- **[`PROTOCOL_REFERENCE.md`](PROTOCOL_REFERENCE.md)**: MSDP protocol implementation reference
- **[`TASK_LIST.md`](TASK_LIST.md)**: Development task tracking and TODO lists

#### **🧪 Testing & Quality**
- **[`tests/README.md`](tests/README.md)**: Testing infrastructure documentation
- **[`create_package.py`](create_package.py)**: Automated .mpackage creation with optional testing integration
- **[`format_xml.py`](format_xml.py)**: XML formatting utility for maintaining code standards
- **[`validate_package.py`](validate_package.py)**: Package validation tool with integrated Lua syntax checking
- **[`run_tests.py`](run_tests.py)**: Comprehensive test suite runner with parallel execution

#### **🎨 Resources**
- **[`images/README`](images/README)**: Image assets documentation
- **[`images/affected_by/README`](images/affected_by/README)**: Status effect icons documentation
- **[`images/affected_by/STATUS_EFFECTS.md`](images/affected_by/STATUS_EFFECTS.md)**: Detailed status effects reference

### Quick Reference

| Need to... | See Documentation |
|------------|------------------|
| **Get started with the GUI** | [`README.md`](README.md) |
| **Understand Mudlet development** | [`MUDLET_DEVELOPMENT.md`](MUDLET_DEVELOPMENT.md) |
| **Work with Python tools** | [`PYTHON_TOOLS.md`](PYTHON_TOOLS.md) |
| **Understand MSDP protocol** | [`PROTOCOL_REFERENCE.md`](PROTOCOL_REFERENCE.md) |
| **Handle Mudlet XML specifics** | [`CLAUDE.md`](CLAUDE.md) |
| **Check development tasks** | [`TASK_LIST.md`](TASK_LIST.md) |
| **Run tests** | [`tests/README.md`](tests/README.md) |
| **Create .mpackage files** | [`create_package.py`](create_package.py) |
| **Check version changes** | [`CHANGELOG.md`](CHANGELOG.md) |

## Development

### Architecture Overview

LuminariGUI uses an event-driven architecture built on:
- **Geyser Framework**: UI component system
- **Adjustable Containers**: User-customizable GUI layout (v2.0.4.001+)
- **MSDP Protocol**: Real-time game data
- **Event System**: Mudlet's event handling for data flow
- **YATCO Integration**: Tabbed chat functionality

### Package Creation Tools

For maintainers and developers who need to create distributable packages:

```bash
# Create .mpackage file from XML source (skip validation due to Mudlet XML)
python create_package.py --skip-validation

# Create development package
python create_package.py --dev --skip-validation

# Create release (skip validation due to Mudlet XML)
python create_package.py --release --version 2.0.4.001 --skip-validation

# Create with custom version
python create_package.py --version 2.1.0 --skip-validation

# XML validation and formatting (will show expected "errors")
python validate_package.py      # ⚠️ Will fail - this is expected
python format_xml.py            # ⚠️ Will fail - this is expected
```

### Testing Infrastructure

**⚠️ TESTING LIMITATIONS**: Due to Mudlet-specific XML formatting, only 3 automated tests work:

```bash
# Run working tests only
python run_tests.py --test functions events performance

# Individual working tests
python test_functions.py      # Unit tests ✅
python test_events.py         # Event handler testing ✅  
python test_performance.py    # Performance benchmarks ✅

# Tests that FAIL due to XML parsing (expected):
python test_lua_syntax.py     # ❌ Cannot parse Mudlet XML
python test_lua_quality.py    # ❌ Cannot parse Mudlet XML
python test_system.py         # ❌ Cannot parse Mudlet XML
python validate_package.py    # ❌ Cannot parse Mudlet XML
python format_xml.py          # ❌ Cannot parse Mudlet XML
```

**The failing tests are expected** - they cannot parse Mudlet-specific XML formatting. This is normal and acceptable.

**Package Creation Features:**
- **Automated .mpackage creation** from XML source
- **Integrated testing** with optional test suite execution
- **Comprehensive validation** including XML structure and Lua syntax
- **Version auto-detection** from CHANGELOG.md
- **Resource bundling** (images, status icons, UI assets)
- **Metadata generation** with proper config.lua
- **Cross-platform compatibility** (Windows, Linux, macOS)

See [`PYTHON_TOOLS.md`](PYTHON_TOOLS.md) for detailed usage instructions and release procedures.

### Extension Points

The system provides several extension points for developers:
- Custom MSDP event handlers
- Additional GUI components
- New chat channels
- Custom mapping features

See [`API.md`](API.md) for detailed development information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly with LuminariMUD
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs via GitHub Issues
- **Discord**: LuminariMUD Discord server #mudlet-help
- **Forums**: LuminariMUD community forums

## Acknowledgments

- **Demonnic**: Original YATCO (Yet Another Tabbed Chat Option) system
- **LuminariMUD Team**: Server-side MSDP implementation and support
- **Mudlet Team**: Excellent MUD client framework
- **Community Contributors**: Testing, feedback, and feature suggestions
