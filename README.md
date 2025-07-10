# LuminariGUI

A comprehensive Mudlet GUI package for LuminariMUD that provides an enhanced gameplay experience through real-time MSDP integration, tabbed chat system, interactive mapping, and advanced status monitoring.

## Features

### 🎮 Core Gameplay Enhancement
- **Real-time MSDP Integration**: Live character stats, room data, and game state updates
- **Advanced Status Monitoring**: Health, movement, experience, and enemy health gauges
- **Action Economy Tracking**: Visual indicators for standard, move, and swift actions
- **Spell Casting Console**: Real-time spell casting progress and status updates

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
   # Download LuminariGUI.xml from the repository
   wget https://github.com/LuminariMUD/LuminariGUI/releases/latest/LuminariGUI.xml
   ```

2. **Install in Mudlet**
   - Open Mudlet
   - Go to `Package Manager` → `Install Package`
   - Select the downloaded `LuminariGUI.xml` file
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
-- Toggle chat gagging from main window
gag chat

-- Toggle self-display in group window  
show self

-- Manual mapping controls
start mapping
stop mapping

-- Debug YATCO chat system
debug
```

### GUI Components

The interface consists of several key areas:

- **Left Panel**: Character information, affects, and group status (tabbed interface)
- **Right Panel**: Map display (Mudlet/ASCII toggle) and legend/room info
- **Bottom Panel**: Chat system and spell casting console
- **Status Bar**: Health, movement, experience gauges with action indicators

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
- Status data: `HEALTH`, `MOVEMENT`, `EXPERIENCE`, `POSITION`
- Combat data: `OPPONENT_HEALTH`, `ACTIONS`
- Environment data: `ROOM`, `GROUP`, `AFFECTS`

## Troubleshooting

### Common Issues

**GUI not appearing after installation:**
- Ensure MSDP is enabled on your character: `msdp`
- Restart Mudlet and reconnect
- Check that you're connected to LuminariMUD (not a test server)

**Chat tabs not working:**
- Use `fixchat` command to reset chat window position
- Check YATCO configuration in the scripts panel

**Mapping not updating:**
- Verify MSDP room data is being received: `debug`
- Use `start mapping` command
- Ensure you're in a mapped area (not wilderness)

**Missing health/movement data:**
- Check MSDP variable reporting is active
- Reconnect to refresh MSDP subscription

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

#### **🏗️ Architecture & Development**
- **[`ARCHITECTURE.md`](ARCHITECTURE.md)**: Detailed system architecture, component relationships, and design patterns
- **[`API.md`](API.md)**: Complete developer API reference with functions, events, and integration patterns
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)**: Development guidelines, coding standards, and contribution workflow

#### **⚙️ Configuration & Setup**
- **[`CONFIGURATION.md`](CONFIGURATION.md)**: Advanced configuration options, customization, and optimization
- **[`DEPLOYMENT.md`](DEPLOYMENT.md)**: Installation procedures, environment setup, and deployment strategies
- **[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)**: Common issues, solutions, and debugging procedures

#### **📋 Project Management**
- **[`CHANGELOG.md`](CHANGELOG.md)**: Version history, feature additions, and breaking changes
- **[`CLAUDE.md`](CLAUDE.md)**: AI development assistance documentation and Claude-specific notes
- **[`LICENSE`](LICENSE)**: MIT License terms and conditions

#### **🔧 Development Tools**
- **[`format_xml.py`](format_xml.py)**: XML formatting utility for maintaining code standards
- **[`validate_xml.py`](validate_xml.py)**: XML validation tool for ensuring package integrity
- **[`.cursorrules`](.cursorrules)**: Cursor IDE configuration and development rules

### Quick Reference

| Need to... | See Documentation |
|------------|------------------|
| **Understand the system** | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| **Develop/extend functionality** | [`API.md`](API.md) |
| **Configure advanced options** | [`CONFIGURATION.md`](CONFIGURATION.md) |
| **Contribute to the project** | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| **Deploy/install** | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| **Fix issues** | [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) |
| **Prepare package for release** | [`PACKAGING.md`](PACKAGING.md) |
| **Check version changes** | [`CHANGELOG.md`](CHANGELOG.md) |

## Development

### Architecture Overview

LuminariGUI uses an event-driven architecture built on:
- **Geyser Framework**: UI component system
- **MSDP Protocol**: Real-time game data
- **Event System**: Mudlet's event handling for data flow
- **YATCO Integration**: Tabbed chat functionality

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
