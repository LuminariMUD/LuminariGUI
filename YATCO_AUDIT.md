# YATCO Audit Report for LuminariGUI

## Overview
This document provides a comprehensive audit of all YATCO (Yet Another Tabbed Chat Object) references in LuminariGUI.xml to support the migration to EMCO.

## Summary Statistics
- **Total `demonnic.chat` references**: 200+
- **Chat append calls**: 8 (7 triggers + 1 function definition)
- **Configuration references**: 60+
- **Window/tab management**: 30+
- **Critical integration points**: 15+

## Critical YATCO API Usage

### 1. Chat Append Calls (Core Functionality)
All chat triggers use the same pattern:
```lua
demonnic.chat:append("TabName")
if GUI.toggles.gagChat == true then
  deleteLineP()
end
```

**Locations:**
- Line 41: `demonnic.chat:append("Tell")` - Tell trigger
- Line 70: `demonnic.chat:append("Congrats")` - Congrats trigger  
- Line 95: `demonnic.chat:append("Chat")` - Chat trigger
- Line 121: `demonnic.chat:append("Say")` - Say trigger
- Line 167: `demonnic.chat:append("Auction")` - Auction trigger
- Line 193: `demonnic.chat:append("Group")` - Group trigger
- Line 219: `demonnic.chat:append("Wiz")` - Wiznet trigger
- Line 4683: Function definition `function demonnic.chat:append(chat)`

### 2. Configuration Properties
YATCO configuration is extensively used throughout:

**Core Settings:**
- `demonnic.chat.use` (line 4239) - Enable/disable chat system
- `demonnic.chat.useContainer` (line 4257) - Container assignment
- `demonnic.chat.config.timestamp` (lines 4266-4267) - Timestamp settings
- `demonnic.chat.config.channels` (line 4306) - Channel list
- `demonnic.chat.config.Alltab` (line 4327) - All tab name
- `demonnic.chat.config.blink` (line 4344) - Blink enable/disable
- `demonnic.chat.config.fontSize` (line 4364) - Font size
- `demonnic.chat.config.gag` (line 4380) - Gag functionality

**Sound Settings:**
- `demonnic.chat.config.soundEnabled` (lines 646, 693, 4353)
- `demonnic.chat.config.soundFile` (lines 709, 4354)
- `demonnic.chat.config.soundVolume` (lines 701, 4355)
- `demonnic.chat.config.soundCooldown` (lines 716, 4356)

**Color Settings:**
- `demonnic.chat.config.activeColors` (line 4401)
- `demonnic.chat.config.inactiveColors` (line 4412)
- `demonnic.chat.config.windowColors` (line 4423)

### 3. Window and Tab Management
YATCO uses complex window/tab structures:

**Core Objects:**
- `demonnic.chat.container` (lines 774, 4612) - Main container
- `demonnic.chat.tabBox` (line 4613) - Tab container
- `demonnic.chat.tabs` (line 4571) - Tab objects
- `demonnic.chat.windows` (line 4572) - Window objects
- `demonnic.chat.currentTab` (line 4449) - Active tab tracking
- `demonnic.chat.tabsToBlink` (line 4570) - Blink tracking

**Key Functions:**
- `demonnic.chat:create()` (line 4623) - Initialize system
- `demonnic.chat:resetUI()` (line 4611) - Reset UI
- `demonnic.chat:showAllTabs()` (line 775) - Show all tabs
- `demonnic.chat:blink()` (lines 635, 4679) - Blink functionality
- `demonnicChatSwitch()` (line 4586) - Tab switching

### 4. Integration Points

**GUI System Integration:**
- `demonnicOnStart()` function (lines 3534, 3669) - Initialization
- `GUI.chatContainerInner` assignment - Container integration
- `fix chat` alias (lines 771-777) - Recovery functionality

**Event Handlers:**
- `sysLoadEvent` - Initialization on load
- Manual refresh in `GUI.initializeOrRefresh()`

**Aliases:**
- `dblink` (lines 629-637) - Toggle blinking
- `dsound` (lines 644-676) - Toggle sound
- `set chat sound` (lines 687-757) - Sound configuration
- `fix chat` (lines 771-777) - Fix chat display

### 5. Custom Modifications

**Channel Color Prefixes:**
Added custom color prefixes for channels (lines 4723-4741):
```lua
local channelColors = {
  Tell = "<gray>[Tell] ",
  Chat = "<yellow>[Chat] ",
  Say = "<green>[Say] ",
  Auction = "<gold>[Auction] ",
  Group = "<cyan>[Group] ",
  Wiz = "<purple>[Wiz] ",
}
```

**Sound Integration:**
Custom sound notification system integrated with YATCO's append function.

## Migration Challenges

### 1. API Differences
- YATCO uses `demonnic.chat:append("TabName")` 
- EMCO uses instance methods like `emcoInstance:append("TabName")`
- Need compatibility layer to maintain existing trigger functionality

### 2. Container Management
- YATCO assigns container via `demonnic.chat.useContainer`
- EMCO requires container in constructor
- Need to handle Adjustable Container integration

### 3. Configuration Structure
- YATCO uses nested config: `demonnic.chat.config.*`
- EMCO may have different configuration approach
- Need to map all configuration options

### 4. Window/Tab Access
- YATCO exposes `demonnic.chat.windows[tab]` and `demonnic.chat.tabs[tab]`
- EMCO may have different internal structure
- Functions like channel color prefixes depend on direct window access

### 5. Function Dependencies
- Multiple functions directly manipulate YATCO internals
- `demonnicChatSwitch()` manages tab switching
- Custom append function with timestamp/color/gag logic

## Recommendations

1. **Create Compatibility Wrapper**: Build a complete API wrapper that maintains `demonnic.chat` interface
2. **Preserve Configuration**: Map all YATCO config options to EMCO equivalents
3. **Test Each Integration**: Verify each trigger, alias, and function works correctly
4. **Maintain User Experience**: Ensure no visible changes to end users
5. **Document Changes**: Create migration guide for any unavoidable differences