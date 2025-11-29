# TASK_LIST.md

## ✅ GUI.init_gauges() Function Analysis - FIXED
**Location: LuminariGUI.xml, Lines 1764-1927**
**Status: All issues have been resolved**

### Summary of Fixes Applied:
1. **CSS Reuse Bug**: Replaced shared CSS objects with inline CSS templates using string.format()
2. **MSDP Integration**: Gauges now initialize with actual MSDP data (HEALTH, PSP, MOVEMENT, OPPONENT_HEALTH)
3. **Error Handling**: Added validation for parent containers (GUI.Bottom, GUI.Box7)
4. **Event Handlers**: Registered MSDP event handlers for automatic gauge updates
5. **Clean Echo Commands**: Removed HTML entities, using proper string formatting
6. **Correct Colors**: Each gauge now displays its intended color (red, turquoise, gold, purple)

### Critical Issues Fixed:

#### 1. **CSS Object Reuse Bug (CRITICAL)**
- **Lines**: 1793-1866
- **Problem**: The same CSS objects (`GUI.GaugeFrontCSS` and `GUI.GaugeBackCSS`) are modified repeatedly for each gauge
- **Impact**: All gauges end up with the Enemy gauge's purple color scheme because each `:set()` call overwrites the previous color
- **Example**:
  ```lua
  GUI.GaugeFrontCSS:set("background-color", "#FF6B6B") -- Health (red)
  GUI.GaugeFrontCSS:set("background-color", "#40E0D0") -- PSP (turquoise) - overwrites!
  GUI.GaugeFrontCSS:set("background-color", "#FFD700") -- Moves (gold) - overwrites!
  GUI.GaugeFrontCSS:set("background-color", "#9370DB") -- Enemy (purple) - final color!
  ```

#### 2. **Hardcoded Initial Values**
- **Lines**: 1832, 1848, 1856, 1864
- **Problem**: All gauges initialized with static values (100/100 or 0/0) instead of actual game data
- **Impact**: Gauges show incorrect values until first update from server

#### 3. **No Error Handling**
- **Entire function**: 1764-1880
- **Problem**: No validation that parent containers exist before creating children
- **Impact**: Potential runtime errors if GUI structure changes

#### 4. **Inefficient CSS Management**
- **Lines**: 1793-1825
- **Problem**: Creates "shared" CSS objects but then modifies them per-gauge, defeating reusability
- **Impact**: Memory inefficiency and confusing code structure

#### 5. **Mixed HTML Entity Usage**
- **Lines**: 1833, 1849, 1857
- **Problem**: Using `&lt;span style = "..."&gt;` HTML entities in echo commands
- **Impact**: May not render correctly in all Mudlet versions

#### 6. **Missing Event Handlers**
- **Entire function**: No event registration
- **Problem**: Gauges created but not connected to MSDP data updates
- **Impact**: Gauges remain static until external code updates them

#### 7. **Fixed Layout Percentages**
- **Lines**: 1827, 1843, 1851, 1859, 1873
- **Problem**: Hardcoded 17% height for gauges, 32% for icons
- **Impact**: Poor adaptability to different screen sizes

### Recommendations:
1. Create separate CSS objects for each gauge or use inline styles
2. Initialize gauges with actual MSDP data or sensible defaults
3. Add error checking for parent container existence
4. Register event handlers for MSDP updates within initialization
5. Consider making heights configurable or responsive

### Code Section Reference:
The complete `GUI.init_gauges()` function spans from line 1764 to line 1880 in LuminariGUI.xml.

---

## 🔧 FUNCTIONAL IMPROVEMENTS - Missing Commands/Features


### Task 10: Add Functional Debug System - MEDIUM COMPLEXITY
- [ ] **Make the existing debug framework actually useful**
  - The debug framework exists but is completely unused
  - Add debug calls to key functions:
    - MSDP data reception: `demonnic:printDebug("msdp", msdp)`
    - Chat message routing: `demonnic:printDebug("chat", {tab=tab, message=line})`
    - Map updates: `demonnic:printDebug("map", {room=room_info})`
    - GUI refresh events: `demonnic:printDebug("gui", "Refreshing " .. component)`
    - Combat events: `demonnic:printDebug("combat", {enemy=opponent_health})`
  - This would make `debug`, `debug list`, and `debugc` commands actually useful

### Task 11: Remove Non-Functional Commands - SIMPLE & SAFE
- [ ] **Clean up vestigial aliases that do nothing**
  - Remove `chaseres` alias - calls non-existent chaser:reset()
  - Remove `mc on` and `mc off` - raise events nothing listens to
  - Keep only working commands to avoid user confusion

### Task 12: Add Missing Utility Commands - SIMPLE & SAFE
- [ ] **Add helpful aliases for common tasks**
  - `clear map` - Clear the current area map (useful for remapping)
  - `save gui` - Save current adjustable container positions manually
  - `reset gui` - Reset all adjustable containers to default positions
  - `list channels` - Show all available chat channels
  - `map info` - Display current room mapping information
  - `gui version` - Show current GUI version

### Task 13: Improve Help System - SIMPLE & SAFE
- [ ] **Add a help command that lists all available commands**
  - `gui help` or just `help gui` - Display all GUI commands with descriptions
  - Group commands by category (Chat, Mapping, Display, Debug, etc.)
  - Include brief description of what each command does
  - Add examples for commands that take parameters

### Task 14: Add Chat History Commands - MEDIUM COMPLEXITY
- [ ] **Add commands to review chat history**
  - `recall <channel>` - Show last N messages from a specific channel
  - `recall all` - Show recent messages from all channels
  - `clear chat <channel>` - Clear a specific chat tab
  - Store limited history (last 100 messages per channel)

### Task 15: Enhanced Mapping Commands - MEDIUM COMPLEXITY
- [ ] **Add more mapping control**
  - `map area <name>` - Set/change current area name
  - `map notes <text>` - Add notes to current room
  - `find room <name>` - Search for rooms by name
  - `map stats` - Show mapping statistics (rooms mapped, areas, etc.)

### Task 16: GUI State Commands - SIMPLE & SAFE
- [ ] **Add commands to check GUI state**
  - `gui status` - Show status of all GUI components
  - `gui refresh <component>` - Refresh specific component (gauges, chat, map, etc.)
  - `toggle <component>` - Show/hide specific GUI components
  - Make troubleshooting easier

---

## 🔧 FUNCTIONAL IMPROVEMENTS - Missing Commands/Features

### Task 9: Add Functional Debug System - MEDIUM COMPLEXITY
- [ ] **Make the existing debug framework actually useful**
  - The debug framework exists but is completely unused
  - Add debug calls to key functions:
    - MSDP data reception: `demonnic:printDebug("msdp", msdp)`
    - Chat message routing: `demonnic:printDebug("chat", {tab=tab, message=line})`
    - Map updates: `demonnic:printDebug("map", {room=room_info})`
    - GUI refresh events: `demonnic:printDebug("gui", "Refreshing " .. component)`
    - Combat events: `demonnic:printDebug("combat", {enemy=opponent_health})`
  - This would make `debug`, `debug list`, and `debugc` commands actually useful

### Task 10: Remove Non-Functional Commands - SIMPLE & SAFE
- [ ] **Clean up vestigial aliases that do nothing**
  - Remove `chaseres` alias - calls non-existent chaser:reset()
  - Remove `mc on` and `mc off` - raise events nothing listens to
  - Keep only working commands to avoid user confusion

### Task 11: Add Missing Utility Commands - SIMPLE & SAFE
- [ ] **Add helpful aliases for common tasks**
  - `clear map` - Clear the current area map (useful for remapping)
  - `save gui` - Save current adjustable container positions manually
  - `reset gui` - Reset all adjustable containers to default positions
  - `list channels` - Show all available chat channels
  - `map info` - Display current room mapping information
  - `gui version` - Show current GUI version

### Task 12: Improve Help System - SIMPLE & SAFE
- [ ] **Add a help command that lists all available commands**
  - `gui help` or just `help gui` - Display all GUI commands with descriptions
  - Group commands by category (Chat, Mapping, Display, Debug, etc.)
  - Include brief description of what each command does
  - Add examples for commands that take parameters

### Task 13: Add Chat History Commands - MEDIUM COMPLEXITY
- [ ] **Add commands to review chat history**
  - `recall <channel>` - Show last N messages from a specific channel
  - `recall all` - Show recent messages from all channels
  - `clear chat <channel>` - Clear a specific chat tab
  - Store limited history (last 100 messages per channel)

### Task 14: Enhanced Mapping Commands - MEDIUM COMPLEXITY
- [ ] **Add more mapping control**
  - `map area <name>` - Set/change current area name
  - `map notes <text>` - Add notes to current room
  - `find room <name>` - Search for rooms by name
  - `map stats` - Show mapping statistics (rooms mapped, areas, etc.)

### Task 15: GUI State Commands - SIMPLE & SAFE
- [ ] **Add commands to check GUI state**
  - `gui status` - Show status of all GUI components
  - `gui refresh <component>` - Refresh specific component (gauges, chat, map, etc.)
  - `toggle <component>` - Show/hide specific GUI components
  - Make troubleshooting easier

---

*This document represents a SIMPLE, SAFE approach to making LuminariGUI look awesome without breaking anything.*