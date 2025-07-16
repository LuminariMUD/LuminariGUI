# LuminariMUD Protocol Reference

## Overview

This document provides a reference for the MSDP (Mud Server Data Protocol) implementation used by LuminariMUD. The protocol enables real-time communication between the MUD server and clients, providing structured data for character stats, world information, and GUI elements.

---


## MSDP Implementation Guide for LuminariGUI

### How MSDP Works in LuminariGUI

#### 1. Initialization Process
When connecting to LuminariMUD, the MSDP protocol is automatically negotiated and initialized:

1. **Protocol Negotiation**: Mudlet negotiates MSDP support with the server during connection
2. **Event Trigger**: When MSDP is enabled, Mudlet fires a `sysProtocolEnabled` event with "MSDP" as the protocol
3. **Variable Registration**: The GUI registers for specific MSDP variables by sending `REPORT` commands:
   ```lua
   sendMSDP("REPORT", "CHARACTER_NAME")
   sendMSDP("REPORT", "HEALTH")
   sendMSDP("REPORT", "HEALTH_MAX")
   -- etc. for all needed variables
   ```

#### 2. State Management
MSDP data is stored in a global `msdp` table that Mudlet automatically maintains:

- **Automatic Updates**: When the server sends MSDP data, Mudlet populates `msdp.VARIABLE_NAME`
- **Event Generation**: Mudlet raises events like `msdp.HEALTH` whenever that variable updates
- **Direct Access**: Scripts can read current values directly: `local hp = msdp.HEALTH`

#### 3. Event-Driven Architecture
The GUI uses anonymous event handlers to react to MSDP updates:

```lua
-- Register handler for health updates
registerAnonymousEventHandler("msdp.HEALTH", "GUI.updateHealthGauge")
registerAnonymousEventHandler("msdp.HEALTH_MAX", "GUI.updateHealthGauge")
   -- etc. for all needed handlers

-- The update function reads from msdp table
function GUI.updateHealthGauge()
  local health = tonumber(msdp.HEALTH) or 0
  local max_health = tonumber(msdp.HEALTH_MAX) or 1
  local pct_health = (health / max_health) * 100
  GUI.Health:setValue(pct_health, 100)
   -- etc. for all needed tables values
end
```

#### 4. Refresh Mechanism
Updates happen automatically when MSDP data changes, but manual refresh is possible:

1. **Automatic**: Server sends update → Mudlet updates `msdp` table → Events fire → UI refreshes
2. **Manual Fix**: The `fix gui` command (when implemented) would:
   - Re-register all event handlers
   - Call all update functions with current MSDP data
   - Useful after errors or UI glitches

#### 5. Example MSDP Variables for GUI

**Core Player Stats:**
- `CHARACTER_NAME`, `LEVEL`, `CLASS`, `RACE`
- `HEALTH` / `HEALTH_MAX`
- `PSP` / `PSP_MAX` (spell points)
- `MOVEMENT` / `MOVEMENT_MAX`

**UI Updates:**
- `GROUP` - JSON array of party members
- `AFFECTS` - JSON array of status effects
- `ACTIONS` - Available action types
- `ROOM` - Current room data (for mapper)

**Combat:**
- `OPPONENT_NAME` / `OPPONENT_HEALTH` / `OPPONENT_HEALTH_MAX`
- `TANK_NAME` / `TANK_HEALTH` / `TANK_HEALTH_MAX`

#### 6. Data Flow Example
```
1. Player takes damage
2. Server sends: MSDP HEALTH 85
3. Mudlet updates: msdp.HEALTH = 85
4. Mudlet raises: "msdp.HEALTH" event
5. GUI.updateHealthGauge() executes
6. Health bar visually updates to 85%
```

#### 7. Troubleshooting MSDP Issues

**No Updates:**
- Check if MSDP is enabled: `display(msdp)`
- Re-send REPORT commands: `sendMSDP("REPORT", "HEALTH")`

**UI Not Refreshing:**
- Event handlers may be disconnected
- Use `fix gui` to re-register handlers
- Check Mudlet error console

**Missing Data:**
- Some variables may not be reported by default
- Send explicit REPORT command for missing variables
- Check server supports the variable (see variable list below)

---




## Protocol Details

**Protocol Version:** 8  
**Source:** KaVir's Protocol Snippet (Public Domain, February 2011)

## Table of Contents

1. [MSDP Variables](#msdp-variables)
2. [Protocol Constants](#protocol-constants)
3. [Data Structures](#data-structures)
4. [Protocol Functions](#protocol-functions)
5. [Color System](#color-system)
6. [GUI Variables](#gui-variables)
7. [Usage Examples](#usage-examples)
8. [Integration Guide](#integration-guide)

## Protocol Constants

### Telnet Options
```c
#define TELOPT_CHARSET  42    // Character set negotiation
#define TELOPT_MSDP     69    // Mud Server Data Protocol
#define TELOPT_MSSP     70    // Mud Server Status Protocol
#define TELOPT_MCCP     86    // Mud Client Compression Protocol v2
#define TELOPT_MSP      90    // Mud Sound Protocol
#define TELOPT_MXP      91    // Mud eXtension Protocol
#define TELOPT_GMCP     201   // Generic Mud Communication Protocol
```

### MSDP Commands
```c
#define MSDP_VAR         1    // Variable name
#define MSDP_VAL         2    // Variable value
#define MSDP_TABLE_OPEN  3    // Start of table
#define MSDP_TABLE_CLOSE 4    // End of table
#define MSDP_ARRAY_OPEN  5    // Start of array
#define MSDP_ARRAY_CLOSE 6    // End of array
#define MAX_MSDP_SIZE    200  // Maximum MSDP packet size
```

### MSSP Commands
```c
#define MSSP_VAR 1    // MSSP variable name
#define MSSP_VAL 2    // MSSP variable value
```

### Configuration Constants
```c
#define SNIPPET_VERSION 8                    // Protocol version
#define MAX_PROTOCOL_BUFFER MAX_RAW_INPUT_LENGTH
#define MAX_VARIABLE_LENGTH 4096
#define MAX_OUTPUT_BUFFER LARGE_BUFSIZE
#define MAX_MSSP_BUFFER 4096
```

## MSDP Variable Enumeration

### Complete Variable List
```c
typedef enum {
    eMSDP_NONE = -1,          // Invalid/unset variable
    
    // General Information
    eMSDP_CHARACTER_NAME,     // Player character name
    eMSDP_SERVER_ID,          // Server identifier 
    eMSDP_SERVER_TIME,        // Current server time
    eMSDP_SNIPPET_VERSION,    // Protocol version number
    
    // Character Statistics  
    eMSDP_AFFECTS,            // Status effects array
    eMSDP_INVENTORY,          // Inventory items array
    eMSDP_ALIGNMENT,          // Character alignment (-1000 to 1000)
    eMSDP_EXPERIENCE,         // Current experience points
    eMSDP_EXPERIENCE_MAX,     // Experience needed for next level
    eMSDP_EXPERIENCE_TNL,     // Experience to next level
    eMSDP_HEALTH,             // Current health points
    eMSDP_HEALTH_MAX,         // Maximum health points
    eMSDP_LEVEL,              // Character level
    eMSDP_RACE,               // Character race
    eMSDP_CLASS,              // Character class
    eMSDP_PSP,                // Current spell points
    eMSDP_PSP_MAX,            // Maximum spell points
    eMSDP_WIMPY,              // Wimpy threshold
    eMSDP_PRACTICE,           // Practice sessions available
    eMSDP_MONEY,              // Gold pieces
    eMSDP_MOVEMENT,           // Current movement points
    eMSDP_MOVEMENT_MAX,       // Maximum movement points
    eMSDP_ATTACK_BONUS,       // Attack bonus modifier
    eMSDP_DAMAGE_BONUS,       // Damage bonus modifier
    eMSDP_AC,                 // Armor class
    
    // Character Attributes (Current)
    eMSDP_STR,                // Current strength
    eMSDP_INT,                // Current intelligence  
    eMSDP_WIS,                // Current wisdom
    eMSDP_DEX,                // Current dexterity
    eMSDP_CON,                // Current constitution
    eMSDP_CHA,                // Current charisma
    
    // Character Attributes (Permanent)
    eMSDP_STR_PERM,           // Permanent strength
    eMSDP_INT_PERM,           // Permanent intelligence
    eMSDP_WIS_PERM,           // Permanent wisdom
    eMSDP_DEX_PERM,           // Permanent dexterity
    eMSDP_CON_PERM,           // Permanent constitution
    eMSDP_CHA_PERM,           // Permanent charisma
    
    // Action Economy
    eMSDP_ACTIONS,            // Available actions array
    eMSDP_STANDARD_ACTION,    // Standard action available (boolean)
    eMSDP_MOVE_ACTION,        // Move action available (boolean)
    eMSDP_SWIFT_ACTION,       // Swift action available (boolean)
    eMSDP_GROUP,              // Group/party data
    eMSDP_POSITION,           // Character position
    
    // Combat Information
    eMSDP_OPPONENT_HEALTH,    // Enemy current health
    eMSDP_OPPONENT_HEALTH_MAX,// Enemy maximum health
    eMSDP_OPPONENT_LEVEL,     // Enemy level
    eMSDP_OPPONENT_NAME,      // Enemy name
    eMSDP_TANK_NAME,          // Tank character name
    eMSDP_TANK_HEALTH,        // Tank current health
    eMSDP_TANK_HEALTH_MAX,    // Tank maximum health
    
    // World Information
    eMSDP_ROOM,               // Complete room data object
    eMSDP_AREA_NAME,          // Current area name
    eMSDP_ROOM_EXITS,         // Available exits array
    eMSDP_ROOM_NAME,          // Current room name
    eMSDP_ROOM_VNUM,          // Room virtual number
    eMSDP_WORLD_TIME,         // In-game time
    eMSDP_SECTORS,            // Terrain/sector data
    eMSDP_MINIMAP,            // ASCII minimap
    
    // Client Configuration
    eMSDP_CLIENT_ID,          // Client identifier (write-once)
    eMSDP_CLIENT_VERSION,     // Client version (write-once)
    eMSDP_PLUGIN_ID,          // Plugin identifier
    eMSDP_ANSI_COLORS,        // ANSI color support (boolean)
    eMSDP_256_COLORS,         // 256 color support (boolean)
    eMSDP_UTF_8,              // UTF-8 support (boolean)
    eMSDP_SOUND,              // Sound support (boolean)
    eMSDP_MXP,                // MXP support (boolean)
    
    // GUI Variables
    eMSDP_BUTTON_1,           // GUI button 1 definition
    eMSDP_BUTTON_2,           // GUI button 2 definition
    eMSDP_BUTTON_3,           // GUI button 3 definition
    eMSDP_BUTTON_4,           // GUI button 4 definition
    eMSDP_BUTTON_5,           // GUI button 5 definition
    eMSDP_GAUGE_1,            // GUI gauge 1 definition
    eMSDP_GAUGE_2,            // GUI gauge 2 definition
    eMSDP_GAUGE_3,            // GUI gauge 3 definition
    eMSDP_GAUGE_4,            // GUI gauge 4 definition
    eMSDP_GAUGE_5,            // GUI gauge 5 definition
    
    eMSDP_MAX                 // Maximum enum value (must be last)
} variable_t;
```

## Data Structures

### Variable Name Structure
```c
typedef struct {
    variable_t Variable;      // The enum type of this variable
    const char *pName;        // The string name of this variable
    bool_t bString;           // Is this variable a string or a number?
    bool_t bConfigurable;     // Can it be configured by the client?
    bool_t bWriteOnce;        // Can only set this variable once
    bool_t bGUI;              // It's a special GUI configuration variable
    int Min;                  // The minimum valid value or string length
    int Max;                  // The maximum valid value or string length
    int Default;              // The default value for a number
    const char *pDefault;     // The default value for a string
} variable_name_t;
```

### MSDP Variable Instance
```c
typedef struct {
    bool_t bReport;           // Is this variable being reported?
    bool_t bDirty;            // Does this variable need to be sent again?
    int ValueInt;             // The numeric value of the variable
    char *pValueString;       // The string value of the variable
} MSDP_t;
```

### Protocol State Structure
```c
typedef struct {
    int WriteOOB;             // Used internally to indicate OOB data
    bool_t Negotiated[eNEGOTIATED_MAX];
    bool_t bIACMode;          // Current mode - deals with broken packets
    bool_t bNegotiated;       // Indicates client successfully negotiated
    bool_t bRenegotiate;      // Workaround for clients that autoconnect
    bool_t bNeedMXPVersion;   // Workaround for clients that autoconnect
    bool_t bBlockMXP;         // Used internally based on MXP version
    bool_t bTTYPE;            // The client supports TTYPE
    bool_t bECHO;             // Toggles ECHO on/off
    bool_t bNAWS;             // The client supports NAWS
    bool_t bCHARSET;          // The client supports CHARSET
    bool_t bMSDP;             // The client supports MSDP
    bool_t bMSSP;             // The client supports MSSP
    bool_t bGMCP;             // The client supports GMCP
    bool_t bMSP;              // The client supports MSP
    bool_t bMXP;              // The client supports MXP
    bool_t bMCCP;             // The client supports MCCP
    support_t b256Support;    // The client supports 256 colors
    int ScreenWidth;          // The client's screen width
    int ScreenHeight;         // The client's screen height
    char *pMXPVersion;        // The version of MXP supported
    char *pLastTTYPE;         // Used for the cyclic TTYPE check
    MSDP_t **pVariables;      // The MSDP variables
} protocol_t;
```

### Support Level Enumeration
```c
typedef enum {
    eUNKNOWN,                 // Support level unknown
    eNO,                      // Feature not supported
    eSOMETIMES,               // Feature partially supported
    eYES                      // Feature fully supported
} support_t;
```

### Negotiated Features
```c
typedef enum {
    eNEGOTIATED_TTYPE,        // Terminal type
    eNEGOTIATED_ECHO,         // Echo control
    eNEGOTIATED_NAWS,         // Negotiate About Window Size
    eNEGOTIATED_CHARSET,      // Character set
    eNEGOTIATED_MSDP,         // Mud Server Data Protocol
    eNEGOTIATED_MSSP,         // Mud Server Status Protocol
    eNEGOTIATED_GMCP,         // Generic Mud Communication Protocol
    eNEGOTIATED_MSP,          // Mud Sound Protocol
    eNEGOTIATED_MXP,          // Mud eXtension Protocol
    eNEGOTIATED_MXP2,         // MXP version 2
    eNEGOTIATED_MCCP,         // Mud Client Compression Protocol
    eNEGOTIATED_MAX           // Maximum value (must be last)
} negotiated_t;
```

## Protocol Functions

### Core Protocol Management
```c
// Create and initialize protocol structure for a user
protocol_t *ProtocolCreate(void);

// Free protocol structure memory
void ProtocolDestroy(protocol_t *apProtocol);

// Negotiate protocols with client
void ProtocolNegotiate(descriptor_t *apDescriptor);

// Process input data and extract protocol sequences
ssize_t ProtocolInput(descriptor_t *apDescriptor, char *apData, int aSize, char *apOut);

// Process output data and apply color codes
const char *ProtocolOutput(descriptor_t *apDescriptor, const char *apData, int *apLength);

// Control echo on/off
void ProtocolNoEcho(descriptor_t *apDescriptor, bool_t abOn);
```

### MSDP Functions
```c
// Update all dirty MSDP variables (call regularly)
void MSDPUpdate(descriptor_t *apDescriptor);

// Flush a specific MSDP variable immediately
void MSDPFlush(descriptor_t *apDescriptor, variable_t aMSDP);

// Send specific MSDP variable to player
void MSDPSend(descriptor_t *apDescriptor, variable_t aMSDP);

// Send custom MSDP variable/value pair
void MSDPSendPair(descriptor_t *apDescriptor, const char *apVariable, const char *apValue);

// Send MSDP variable as an array
void MSDPSendList(descriptor_t *apDescriptor, const char *apVariable, const char *apValue);

// Set numeric MSDP variable value
void MSDPSetNumber(descriptor_t *apDescriptor, variable_t aMSDP, int aValue);

// Set string MSDP variable value
void MSDPSetString(descriptor_t *apDescriptor, variable_t aMSDP, const char *apValue);

// Set MSDP variable as table
void MSDPSetTable(descriptor_t *apDescriptor, variable_t aMSDP, const char *apValue);

// Set MSDP variable as array
void MSDPSetArray(descriptor_t *apDescriptor, variable_t aMSDP, const char *apValue);
```

### Copyover Support
```c
// Get protocol state as string for copyover
const char *CopyoverGet(descriptor_t *apDescriptor);

// Restore protocol state from copyover string
void CopyoverSet(descriptor_t *apDescriptor, const char *apData);
```

### MXP Functions
```c
// Create MXP tag if supported
const char *MXPCreateTag(descriptor_t *apDescriptor, const char *apTag);

// Send MXP tag directly to user
void MXPSendTag(descriptor_t *apDescriptor, const char *apTag);
```

### Sound Functions
```c
// Send sound trigger using MSDP/GMCP/MSP
void SoundSend(descriptor_t *apDescriptor, const char *apTrigger);
```

### Unicode Functions
```c
// Get UTF-8 sequence for unicode value
char *UnicodeGet(int aValue);

// Add UTF-8 sequence to string
void UnicodeAdd(char **apString, int aValue);
```

## Color System

### Predefined Color Codes
The protocol uses tab (`\t`) as the color escape character:

#### Basic Colors
- `n`: no colour (switches colour off)
- `r`: dark red, `R`: light red
- `g`: dark green, `G`: light green  
- `b`: dark blue, `B`: light blue
- `y`: dark yellow, `Y`: light yellow
- `m`: dark magenta, `M`: light magenta
- `c`: dark cyan, `C`: light cyan
- `w`: dark white, `W`: light white

#### Extended Colors
- `a`: dark azure, `A`: light azure
- `j`: dark jade, `J`: light jade
- `l`: dark lime, `L`: light lime
- `o`: dark orange, `O`: bright orange
- `p`: dark pink, `P`: light pink
- `t`: dark tan, `T`: light tan
- `v`: dark violet, `V`: light violet
- `d`: dark grey/black, `D`: light grey

#### Formatting
- `_`: underlined (if supported)
- `+`: bold (if supported)
- `-`: blinking (if supported)
- `=`: reverse (if supported)
- `*`: at-sign

#### Palettes
- `1`: base palette 1
- `2`: base palette 2
- `3`: base palette 3

### RGB Color Specification
```
\t[F010]  // Very dark green foreground
\t[B530]  // Orange background
```
Format: `[F/B][0-5][0-5][0-5]` where:
- First character: `F` (foreground) or `B` (background)
- Next three: RGB values from 0-5 each

### Unicode Characters
```
\t[U9973/B]  // Boat symbol (fallback: B)
\t[U9814/C]  // Rook symbol (fallback: C)
```
Format: `[U<decimal>/<fallback>]` where:
- `U`: Indicates unicode
- `<decimal>`: Unicode character number
- `<fallback>`: ASCII fallback (up to 7 characters)

### Color Functions
```c
// Convert RGB values to color escape sequence
const char *ColourRGB(descriptor_t *apDescriptor, const char *apRGB);
```

## MSDP Variables

### General Information
| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `CHARACTER_NAME` | String | Character's name | "Gandalf" |
| `SERVER_ID` | String | Server identifier | "LuminariMUD" |
| `SERVER_TIME` | Number | Server timestamp | 1234567890 |
| `SNIPPET_VERSION` | Number | Protocol version | 2 |

### Character Statistics
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `HEALTH` | Number | Current health points | 0-999999 |
| `HEALTH_MAX` | Number | Maximum health points | 1-999999 |
| `PSP` | Number | Current spell points | 0-999999 |
| `PSP_MAX` | Number | Maximum spell points | 1-999999 |
| `MOVEMENT` | Number | Current movement points | 0-999999 |
| `MOVEMENT_MAX` | Number | Maximum movement points | 1-999999 |
| `EXPERIENCE` | Number | Current experience | 0-999999999 |
| `EXPERIENCE_MAX` | Number | Experience needed for next level | 1-999999999 |
| `EXPERIENCE_TNL` | Number | Experience to next level | 0-999999999 |
| `LEVEL` | Number | Character level | 1-30 |
| `ALIGNMENT` | Number | Character alignment | -1000 to 1000 |
| `WIMPY` | Number | Wimpy setting | 0-100 |
| `PRACTICE` | Number | Practice sessions available | 0-999 |
| `MONEY` | Number | Gold pieces | 0-999999999 |

### Character Attributes
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `STR` | Number | Current strength | 1-50 |
| `INT` | Number | Current intelligence | 1-50 |
| `WIS` | Number | Current wisdom | 1-50 |
| `DEX` | Number | Current dexterity | 1-50 |
| `CON` | Number | Current constitution | 1-50 |
| `CHA` | Number | Current charisma | 1-50 |
| `STR_PERM` | Number | Permanent strength | 1-50 |
| `INT_PERM` | Number | Permanent intelligence | 1-50 |
| `WIS_PERM` | Number | Permanent wisdom | 1-50 |
| `DEX_PERM` | Number | Permanent dexterity | 1-50 |
| `CON_PERM` | Number | Permanent constitution | 1-50 |
| `CHA_PERM` | Number | Permanent charisma | 1-50 |

### Combat Statistics
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `ATTACK_BONUS` | Number | Attack bonus | -50 to 100 |
| `DAMAGE_BONUS` | Number | Damage bonus | -50 to 100 |
| `AC` | Number | Armor class | -50 to 50 |

### Character Information
| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `RACE` | String | Character race | "Human", "Elf", "Dwarf" |
| `CLASS` | String | Character class | "Wizard", "Fighter", "Cleric" |
| `POSITION` | String | Character position | "standing", "sitting", "fighting" |
| `AFFECTS` | String | Status effects | JSON array |
| `INVENTORY` | String | Inventory items | JSON array |

### Action Economy
| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ACTIONS` | String | Available actions | JSON array |
| `STANDARD_ACTION` | Boolean | Standard action available | true |
| `MOVE_ACTION` | Boolean | Move action available | true |
| `SWIFT_ACTION` | Boolean | Swift action available | true |

### Group/Party Information
| Variable | Type | Description | Format |
|----------|------|-------------|--------|
| `GROUP` | String | Group member data | JSON array |

### Combat Information
| Variable | Type | Description | Range |
|----------|------|-------------|-------|
| `OPPONENT_HEALTH` | Number | Enemy health | 0-999999 |
| `OPPONENT_HEALTH_MAX` | Number | Enemy max health | 1-999999 |
| `OPPONENT_LEVEL` | Number | Enemy level | 1-100 |
| `OPPONENT_NAME` | String | Enemy name | "Orc Warrior" |
| `TANK_NAME` | String | Tank's name | "Defender" |
| `TANK_HEALTH` | Number | Tank's health | 0-999999 |
| `TANK_HEALTH_MAX` | Number | Tank's max health | 1-999999 |

### World Information
| Variable | Type | Description | Format |
|----------|------|-------------|--------|
| `ROOM` | String | Complete room data | JSON object |
| `AREA_NAME` | String | Current area name | "The Forest of Shadows" |
| `ROOM_EXITS` | String | Available exits | JSON array |
| `ROOM_NAME` | String | Room name | "A Dark Forest Path" |
| `ROOM_VNUM` | Number | Room virtual number | 1-999999 |
| `WORLD_TIME` | Number | In-game time | 0-23 |
| `SECTORS` | String | Terrain types | JSON array |
| `MINIMAP` | String | ASCII minimap | Multi-line string |

### Client Configuration
| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `CLIENT_ID` | String | Client identifier | Write-once |
| `CLIENT_VERSION` | String | Client version | Write-once |
| `PLUGIN_ID` | String | Plugin identifier | Configurable |
| `ANSI_COLORS` | Boolean | ANSI color support | true |
| `256_COLORS` | Boolean | 256 color support | false |
| `UTF_8` | Boolean | UTF-8 support | false |
| `SOUND` | Boolean | Sound support | false |
| `MXP` | Boolean | MXP support | false |

## GUI Variables

LuminariMUD provides GUI variable definitions for generic client interfaces:

### Buttons
| Variable | Label | Command | Description |
|----------|-------|---------|-------------|
| `BUTTON_1` | Help | help | Access help system |
| `BUTTON_2` | Look | look | Look around |
| `BUTTON_3` | Score | help | View character score |
| `BUTTON_4` | Equipment | equipment | View equipment |
| `BUTTON_5` | Inventory | inventory | View inventory |

### Gauges
| Variable | Label | Color | Current | Maximum | Description |
|----------|-------|-------|---------|---------|-------------|
| `GAUGE_1` | Health | red | HEALTH | HEALTH_MAX | Health bar |
| `GAUGE_2` | PSP | blue | PSP | PSP_MAX | Spell points |
| `GAUGE_3` | Movement | green | MOVEMENT | MOVEMENT_MAX | Movement points |
| `GAUGE_4` | Exp TNL | yellow | EXPERIENCE | EXPERIENCE_MAX | Experience to level |
| `GAUGE_5` | Opponent | darkred | OPPONENT_HEALTH | OPPONENT_HEALTH_MAX | Enemy health |

## Data Types

### String Types
- **JSON Arrays**: `["item1", "item2", "item3"]`
- **JSON Objects**: `{"key": "value", "number": 42}`
- **Plain Text**: Simple string values

### Number Types
- **Integers**: Whole numbers (e.g., 100, -50, 0)
- **Ranges**: Defined minimum and maximum values

### Boolean Types
- **Values**: 0 (false) or 1 (true)

## Room Data Structure

The `ROOM` variable contains a comprehensive JSON object:

```json
{
  "VNUM": 12345,
  "NAME": "A Dark Forest Path",
  "AREA": "The Forest of Shadows", 
  "ENVIRONMENT": "forest",
  "TERRAIN": "path",
  "EXITS": {
    "north": 12346,
    "south": 12344,
    "east": 12350
  },
  "ITEMS": ["sword", "torch"],
  "MOBS": ["orc warrior", "forest sprite"]
}
```

## Affects Data Structure

The `AFFECTS` variable contains an array of status effects:

```json
[
  {
    "name": "hasted",
    "duration": 120,
    "type": "beneficial"
  },
  {
    "name": "poison",
    "duration": 45,
    "type": "detrimental"
  }
]
```

## Group Data Structure

The `GROUP` variable contains party member information:

```json
[
  {
    "name": "Gandalf",
    "health": 250,
    "health_max": 300,
    "level": 15,
    "class": "Wizard",
    "position": "standing"
  },
  {
    "name": "Aragorn", 
    "health": 180,
    "health_max": 200,
    "level": 12,
    "class": "Ranger",
    "position": "fighting"
  }
]
```

## Usage Examples

### Basic Client Implementation

```lua
-- Register for MSDP events
registerAnonymousEventHandler("msdp.HEALTH", function()
  local health = msdp.HEALTH or 0
  local maxHealth = msdp.HEALTH_MAX or 1
  updateHealthBar(health, maxHealth)
end)

-- Handle room changes
registerAnonymousEventHandler("msdp.ROOM", function()
  if msdp.ROOM then
    local roomData = yajl.to_value(msdp.ROOM)
    updateRoomDisplay(roomData)
  end
end)

-- Process affects
registerAnonymousEventHandler("msdp.AFFECTS", function()
  if msdp.AFFECTS then
    local affects = yajl.to_value(msdp.AFFECTS)
    updateStatusEffects(affects)
  end
end)
```

### Advanced Data Processing

```lua
-- Safe data access with validation
function getSafeMSDPValue(key, defaultValue, dataType)
  local value = msdp[key]
  
  if value == nil then
    return defaultValue
  end
  
  if dataType == "number" then
    local num = tonumber(value)
    return num or defaultValue
  elseif dataType == "json" then
    local success, result = pcall(yajl.to_value, value)
    return success and result or defaultValue
  else
    return tostring(value)
  end
end

-- Example usage
local health = getSafeMSDPValue("HEALTH", 0, "number")
local affects = getSafeMSDPValue("AFFECTS", {}, "json")
local roomName = getSafeMSDPValue("ROOM_NAME", "Unknown", "string")
```

## Integration Guide

### Setting Up MSDP

1. **Enable MSDP in client**: Send MSDP negotiation sequence
2. **Request variables**: Use `MSDP_REQUEST` to subscribe to specific variables
3. **Handle updates**: Register event handlers for variable changes
4. **Parse data**: Convert JSON strings to usable data structures

### Best Practices

1. **Validate data**: Always check for nil values and validate data types
2. **Use safe parsing**: Wrap JSON parsing in pcall() to handle malformed data
3. **Cache frequently used data**: Store processed data to avoid repeated parsing
4. **Handle disconnections**: Reset MSDP data when connection is lost
5. **Error boundaries**: Isolate MSDP processing to prevent crashes

### Performance Considerations

1. **Selective subscriptions**: Only request variables you actually use
2. **Efficient parsing**: Parse JSON data only when it changes
3. **Debounce updates**: Avoid excessive UI updates for rapidly changing values
4. **Memory management**: Clean up event handlers and cached data appropriately

## Protocol Constants

### MSDP Commands
- `MSDP_VAL`: Variable value
- `MSDP_VAR`: Variable name  
- `MSDP_TABLE_OPEN`: Start of table
- `MSDP_TABLE_CLOSE`: End of table
- `MSDP_ARRAY_OPEN`: Start of array
- `MSDP_ARRAY_CLOSE`: End of array

### Telnet Constants
- `IAC`: Interpret As Command (255)
- `SB`: Subnegotiation Begin (250)
- `SE`: Subnegotiation End (240)
- `MSDP`: MSDP option code (69)

This reference provides the foundation for implementing MSDP support in MUD clients, particularly for LuminariGUI integration with LuminariMUD servers.