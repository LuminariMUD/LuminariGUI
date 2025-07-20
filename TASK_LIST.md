# TASK_LIST.md

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