# LuminariGUI Quick Reference

## Installation Commands

### Automatic Installation (Currently Disabled)
```bash
# Simply connect to LuminariMUD
Host: luminarimud.com
Port: 4100
# Package auto-installs via GMCP when available
```

### Manual Installation
```bash
# Download and install
wget https://github.com/LuminariMUD/LuminariGUI/releases/latest/LuminariGUI.xml
# Import into Mudlet: Package Manager → Install Package
```

## Essential In-Game Commands
```lua
-- Enable MSDP (required for GUI)
msdp

-- Chat system controls
gag chat              -- Toggle chat gagging from main window
show self             -- Toggle self in group display

-- Debug and troubleshooting
debug                 -- Toggle debug output
debug list            -- List debug categories
debugc msdp           -- Watch MSDP debug messages
```

## Development Commands

### Validation & Testing
```bash
# Validate package (XML structure and Lua syntax)
python3 validate_package.py

# Run complete test suite
python3 run_tests.py

# Run specific tests
python3 run_tests.py --test syntax      # Lua syntax only
python3 run_tests.py --test quality     # Static analysis
python3 run_tests.py --test functions   # Unit tests
python3 run_tests.py --test performance # Benchmarks

# Individual test tools
python3 test_lua_syntax.py              # Syntax validation
python3 test_lua_quality.py             # Code quality analysis
```

### Package Management
```bash
# Format XML file (creates backup)
python3 format_xml.py

# Format without backup
python3 format_xml.py --no-backup

# Create package with testing
python3 create_package.py --run-tests

# Full release with testing
python3 create_package.py --release --run-tests
```

## GUI Components

### Main Interface Areas
- **Left Panel**: Character info, affects, group status (tabbed)
- **Right Panel**: Map display and room info
- **Bottom Panel**: Chat system and spell console
- **Status Bar**: Health, movement, experience gauges

### Status Effect Icons
- **90+ Icons**: Automatically display active effects
- **Categories**: Defensive, vision, combat, movement, concealment, debuffs
- **Real-time**: Updates via MSDP protocol

## Troubleshooting

### GUI Not Appearing
```lua
-- Check MSDP is enabled
msdp

-- Restart Mudlet and reconnect
-- Verify connection to LuminariMUD (not test server)
```

### Chat Issues
```lua
-- Reset chat window
fixchat

-- Check YATCO configuration in scripts panel
```

### Mapping Problems
```lua
-- Enable mapping
start mapping

-- Check MSDP room data
debug
debugc msdp

-- Ensure you're in mapped area (not wilderness)
```

### Performance Issues
```lua
-- Disable debug mode
LuminariGUI.debug = false

-- Check system resources
-- Reduce GUI update frequency if needed
```

## Key Features

### Real-time Updates
- Character stats (health, movement, experience)
- Group member status
- Combat information
- Room and environment data

### Chat System
- Tabbed interface for different channels
- Tell, Chat, Group, Auction, Congrats, Wizard
- Message filtering and notification system

### Mapping
- Automatic room creation via MSDP
- Color-coded terrain types
- Interactive map legend
- Speedwalking support

### Status Monitoring
- Visual affect tracking with icons
- Combat mode indicators
- Action economy display
- Spell casting progress

## Getting Help

- **Documentation**: See README.md and other .md files
- **Issues**: Report bugs via GitHub Issues  
- **Discord**: LuminariMUD Discord #mudlet-help
- **Forums**: LuminariMUD community forums

## File Structure
```
LuminariGUI/
├── LuminariGUI.xml          # Main package file
├── README.md                # Full documentation
├── CLAUDE.md                # AI development guide
├── validate_xml.py          # XML validation tool
├── format_xml.py            # XML formatting tool
└── images/                  # UI assets
    └── affected_by/         # Status effect icons (90 files)
```