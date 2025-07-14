# TASK_LIST.md - List of Tasks and TODO Items for LuminariGUI

## ✅ COMPLETED PLAN: Comprehensive Testing Issue Resolution

### Summary of Issues Found
**All tests are passing** but there were **249 warnings** total across different categories:
- **13 Lua syntax warnings** (style issues)
- **236 Lua quality warnings** (code quality issues)
- **6 resource leaks** (potential memory leaks)

### Implementation Completed

**Phase 1 (Critical)** ✅:
1. ✅ Updated luacheck configuration with all missing Mudlet API functions
2. ✅ Added missing globals to reduce false positives (reduced warnings from 236 to 4)
3. ✅ Created whitelist for intentional global variables

**Phase 2 (Important)** ✅:
1. ✅ Fixed function keyword spacing issues (7 occurrences)
2. ✅ Fixed 'end)' pattern issues where appropriate (3 of 6 fixed, 3 remain as acceptable inline patterns)
3. ✅ Removed all unused variables (4 legitimate issues fixed)

**Phase 3 (Resource Management)** ✅:
1. ✅ Implemented comprehensive resource cleanup system
2. ✅ Added tracking for all event handlers and timers
3. ✅ Created automatic cleanup on package uninstall/exit

### Final Results
- **Syntax warnings**: 13 → 3 (only acceptable inline patterns remain)
- **Quality warnings**: 236 → 0 
- **Resource leaks**: Comprehensive cleanup system implemented
- **Test output**: Clean and easy to read
- **Code maintainability**: Significantly improved

See TESTING_IMPROVEMENTS_SUMMARY.md for full details.

------------------------------------------------------------------------------------------------------------

## Senior-Level Code Audit Results - Root Cause Analysis

### CRITICAL SYSTEMIC ISSUES (Causing Cascading Failures)

#### **CRITICAL** - Fragile Event System Architecture
**Root Cause:** Uncontrolled event propagation with no dependency management
**Symptoms:** Fixing one component breaks others due to event cascade failures
**Evidence:** 
- 15+ `registerAnonymousEventHandler()` calls with no cleanup tracking
- MSDP events (`msdp.ROOM`, `msdp.AFFECTS`, `msdp.GROUP`) trigger multiple handlers simultaneously
- No event ordering or dependency resolution
- Event handlers can fail silently, breaking dependent systems

**Impact:** **HIGH** - This is the primary source of "fix one, break another" instability
**Fix Strategy:** Implement centralized event bus with dependency tracking and error isolation

#### **CRITICAL** - Shared Global State Corruption
**Root Cause:** Multiple systems write to shared globals without synchronization
**Symptoms:** State inconsistencies cause unpredictable behavior
**Evidence:**
- `GUI.toggles`, `msdp`, `map.room_info` accessed by multiple systems
- No state validation or rollback mechanisms
- MSDP data can be partially updated, leaving inconsistent state
- Race conditions between map updates and UI refreshes

**Impact:** **HIGH** - Changes to one system corrupt state for others
**Fix Strategy:** Implement immutable state patterns with validation

#### **CRITICAL** - Resource Lifecycle Management Failure
**Root Cause:** No coordinated cleanup of timers, handlers, and UI elements
**Symptoms:** Memory leaks and orphaned resources cause system degradation
**Evidence:**
- Timer cleanup with `killTimer()` only in some paths
- Event handlers registered but never cleaned up
- UI elements created but not properly destroyed
- `tempTimer()` calls without corresponding cleanup

**Impact:** **HIGH** - System becomes unstable over time
**Fix Strategy:** Implement RAII patterns with automatic cleanup

### HIGH PRIORITY ARCHITECTURAL FLAWS

#### **HIGH** - Missing Error Boundaries
**Root Cause:** Errors propagate unconstrained across system boundaries
**Symptoms:** Single component failure cascades to unrelated systems
**Evidence:**
- Limited use of `pcall()` for error containment
- No error recovery mechanisms
- Exception in one MSDP handler can break entire mapping system
- UI errors corrupt non-UI state

**Impact:** One small bug can bring down entire GUI
**Fix Strategy:** Implement error boundaries with graceful degradation

#### **HIGH** - Tight Coupling Between Components
**Root Cause:** Direct dependencies between unrelated systems
**Symptoms:** Cannot modify one system without affecting others
**Evidence:**
- Mapping system directly manipulates GUI elements
- Chat system depends on mapping state
- Button system tightly coupled to cast console
- No abstraction layers or interfaces

**Impact:** Maintenance nightmare - every change is risky
**Fix Strategy:** Implement loose coupling with message passing

#### **HIGH** - Initialization Race Conditions
**Root Cause:** Components initialize in unpredictable order
**Symptoms:** Intermittent startup failures and inconsistent behavior
**Evidence:**
- GUI elements created before dependencies are ready
- MSDP handlers registered before protocol negotiation
- No dependency declaration or initialization ordering
- `tempTimer()` delays used as band-aids

**Impact:** Unpredictable system behavior on startup
**Fix Strategy:** Implement dependency injection with ordered initialization

### MEDIUM PRIORITY STABILITY ISSUES

#### **MEDIUM** - Inadequate Input Validation
**Root Cause:** External data (MSDP, user input) processed without validation
**Symptoms:** Malformed data causes system corruption
**Evidence:**
- Direct access to `msdp.ROOM` without nil checks
- User input processed without sanitization
- No bounds checking on array access
- Assumes well-formed data structures

**Impact:** External data corruption can crash system
**Fix Strategy:** Implement comprehensive input validation

#### **MEDIUM** - Inconsistent Error Handling Patterns
**Root Cause:** No standardized error handling approach
**Symptoms:** Unpredictable error behavior across components
**Evidence:**
- Mix of `pcall()`, direct calls, and silent failures
- Some errors logged, others ignored
- No consistent error recovery strategy
- Different error handling in similar functions

**Impact:** Debugging is difficult, errors unpredictable
**Fix Strategy:** Standardize error handling patterns

#### **MEDIUM** - Performance Anti-Patterns
**Root Cause:** Inefficient algorithms in hot paths
**Symptoms:** System becomes sluggish, affecting responsiveness
**Evidence:**
- O(n) room positioning algorithm runs frequently
- Redundant font size calculations
- No caching of expensive operations
- String concatenation in loops

**Impact:** System responsiveness degrades over time
**Fix Strategy:** Optimize hot paths with caching and better algorithms

### LOW PRIORITY QUALITY ISSUES

#### **LOW** - Monolithic Function Design
**Root Cause:** Large functions with multiple responsibilities
**Symptoms:** Difficult to test, debug, and maintain
**Evidence:**
- Functions exceeding 50 lines with mixed concerns
- Single functions handling multiple unrelated tasks
- No separation of concerns
- Difficult to isolate issues

**Impact:** Maintenance difficulty, hard to locate bugs
**Fix Strategy:** Break into smaller, focused functions

#### **LOW** - Inconsistent Coding Standards
**Root Cause:** No enforced coding standards
**Symptoms:** Code is harder to read and maintain
**Evidence:**
- Mixed naming conventions (camelCase, snake_case)
- Inconsistent indentation
- No documentation standards
- Magic numbers throughout code

**Impact:** Reduced maintainability and readability
**Fix Strategy:** Establish and enforce coding standards

### IMMEDIATE STABILIZATION RECOMMENDATIONS

#### Phase 1: Stop the Bleeding (1-2 weeks)
1. **Add Error Boundaries:** Wrap all event handlers in `pcall()` with error logging
2. **Implement Resource Cleanup:** Track and clean up all timers and handlers
3. **Add State Validation:** Validate all shared state before use
4. **Fix Initialization Order:** Ensure dependencies are available before use

#### Phase 2: Structural Improvements (2-4 weeks)
1. **Implement Event Bus:** Centralize event handling with dependency tracking
2. **Add State Management:** Implement immutable state with validation
3. **Create Abstraction Layers:** Decouple components with interfaces
4. **Add Comprehensive Logging:** Track system state and errors

#### Phase 3: Long-term Stability (4-6 weeks)
1. **Implement Testing:** Add unit tests for critical functions
2. **Add Performance Monitoring:** Track resource usage and performance
3. **Create Documentation:** Document system architecture and dependencies
4. **Implement Graceful Degradation:** System should work even with component failures

### CONCLUSION

The root cause of your "fix one, break another" cycle is a lack of **system boundaries** and **dependency management**. The codebase has evolved into a tightly coupled system where changes ripple unpredictably through shared state and event handling.

**Priority Order:**
1. **Event System Redesign** - This is the biggest source of instability
2. **State Management** - Prevents corruption that causes cascading failures  
3. **Resource Management** - Stops memory leaks and orphaned resources
4. **Error Boundaries** - Contains failures to prevent system-wide crashes

This audit reveals that stability requires **architectural changes**, not just bug fixes. The current architecture makes every change risky because there are no isolation boundaries between components.

------------------------------------------------------------------------------------------------------------

## Advanced Window Management Implementation Plan

### Overview
Add detachable window functionality to LuminariGUI based on patterns extracted from example_mudlet_GUI.xml. This will allow players to detach GUI panels into separate windows for multi-monitor setups.

### Phase 1: Core Infrastructure

#### Task 1.1: Add Character Data Persistence System
**File:** `LuminariGUI.xml` - New Script "CharacterData"
**Priority:** HIGH

```lua
-- Character data persistence system (similar to charData from example)
LUM = LUM or {}
LUM.data = LUM.data or {}

function LUM.data:get(key, default)
  if not self.store then
    self:load()
  end
  return self.store[key] or default
end

function LUM.data:set(key, value, save)
  if not self.store then
    self.store = {}
  end
  self.store[key] = value
  if save then
    self:save()
  end
end

function LUM.data:save()
  local filename = getMudletHomeDir() .. "/LuminariGUI_data.lua"
  table.save(filename, self.store)
end

function LUM.data:load()
  local filename = getMudletHomeDir() .. "/LuminariGUI_data.lua"
  if io.exists(filename) then
    self.store = table.load(filename) or {}
  else
    self.store = {}
  end
end
```

#### Task 1.2: Create Detachable Window Base Class
**File:** `LuminariGUI.xml` - New Script "DetachableWindow"
**Priority:** HIGH

```lua
-- Detachable window manager
LUM.DetachableWindow = LUM.DetachableWindow or {}

function LUM.DetachableWindow:new(container, name)
  local obj = {
    container = container,
    name = name,
    isDetached = false,
    userWindow = nil,
    originalParent = container.parent,
    originalGeometry = {}
  }
  setmetatable(obj, {__index = self})
  
  -- Add double-click handler to header if it exists
  if container.header then
    container.header:setDoubleClickCallback(function()
      obj:toggle()
    end)
  end
  
  -- Restore previous state
  if LUM.data:get("window_" .. name .. "_detached", false) then
    obj:detach()
  end
  
  return obj
end

function LUM.DetachableWindow:toggle()
  if self.isDetached then
    self:attach()
  else
    self:detach()
  end
end

function LUM.DetachableWindow:detach()
  if self.isDetached then return end
  
  -- Store original geometry
  self.originalGeometry = {
    x = self.container:get_x(),
    y = self.container:get_y(),
    width = self.container:get_width(),
    height = self.container:get_height()
  }
  
  -- Create user window
  self.userWindow = Geyser.UserWindow:new({
    name = self.name .. "_detached",
    x = self.originalGeometry.x,
    y = self.originalGeometry.y,
    width = self.originalGeometry.width,
    height = self.originalGeometry.height
  })
  
  -- Move container to user window
  self.container:changeContainer(self.userWindow)
  self.container:resize("100%", "100%")
  self.container:move(0, 0)
  
  self.isDetached = true
  LUM.data:set("window_" .. self.name .. "_detached", true, true)
  
  cecho("<green>Window '" .. self.name .. "' detached. Double-click header to reattach.\n")
end

function LUM.DetachableWindow:attach()
  if not self.isDetached then return end
  
  -- Hide user window
  if self.userWindow then
    self.userWindow:hide()
    self.userWindow = nil
  end
  
  -- Move container back to original parent
  self.container:changeContainer(self.originalParent)
  self.container:resize(self.originalGeometry.width, self.originalGeometry.height)
  self.container:move(self.originalGeometry.x, self.originalGeometry.y)
  
  self.isDetached = false
  LUM.data:set("window_" .. self.name .. "_detached", false, true)
  
  cecho("<yellow>Window '" .. self.name .. "' reattached to main GUI.\n")
end
```

### Phase 2: Window Conversion System

#### Task 2.1: Add Header Styling for Detachable Windows
**File:** `LuminariGUI.xml` - Modify "TabbedInfoWindow" script
**Priority:** MEDIUM

```lua
-- Add visual indication for detachable headers
GUI.DetachableHeaderCSS = CSSMan.new([[
  background-color: rgba(60,60,60,255);
  border: 1px solid rgb(140,140,140);
  color: white;
  font-family: Tahoma, Geneva, sans-serif;
  qproperty-wordWrap: true;
]])

-- Modify tabbedInfoWindow.init() function to add detachable styling
function GUI.tabbedInfoWindow.init()
  -- ... existing code ...
  
  -- Make the info window detachable
  GUI.tabbedInfoWindow.detachable = LUM.DetachableWindow:new(
    GUI.tabbedInfoWindow.container, 
    "InfoWindow"
  )
  
  -- Add visual feedback to header
  GUI.tabbedInfoWindow.header:setStyleSheet(GUI.DetachableHeaderCSS:getCSS())
  GUI.tabbedInfoWindow.header:setToolTip("Double-click to detach/attach window")
  
  -- ... rest of existing code ...
end
```

#### Task 2.2: Make Chat Window Detachable
**File:** `LuminariGUI.xml` - Modify "Boxes" script
**Priority:** HIGH

```lua
-- In GUI.init_boxes() function, after chatContainer creation:
function GUI.init_boxes()
  -- ... existing code ...
  
  -- Create chat container with detachable header
  GUI.chatContainer = Geyser.Label:new({
    name = "GUI.chatContainer",
    x = 8,
    y = "15%", 
    width = GUI.Box2:get_width() - 14,
    height = "70%",
  }, GUI.Box2)
  
  -- Add header for chat window
  GUI.chatHeader = Geyser.Label:new({
    name = "GUI.chatHeader",
    x = 0, y = 0,
    width = "100%", height = 25
  }, GUI.chatContainer)
  
  GUI.chatHeader:setStyleSheet(GUI.DetachableHeaderCSS:getCSS())
  GUI.chatHeader:echo("<center>Chat - Double-click to detach")
  GUI.chatHeader:setToolTip("Double-click to detach/attach chat window")
  
  -- Adjust chat content area
  demonnic.chat.useContainer = Geyser.Container:new({
    name = "GUI.chatContent",
    x = 0, y = 25,
    width = "100%", height = "100%-25"
  }, GUI.chatContainer)
  
  -- Make chat window detachable
  GUI.chatDetachable = LUM.DetachableWindow:new(GUI.chatContainer, "ChatWindow")
  
  -- ... rest of existing code ...
end
```

#### Task 2.3: Make Button Window Detachable
**File:** `LuminariGUI.xml` - Modify "Button" script
**Priority:** MEDIUM

```lua
-- In GUI.buttonWindow.init() function:
function GUI.buttonWindow.init()
  -- ... existing code ...
  
  -- Add header to button window
  GUI.buttonWindow.header = Geyser.Label:new({
    name = "GUI.buttonWindow.header",
    x = 0, y = 0,
    width = "100%", height = 20
  }, GUI.buttonWindow.container)
  
  GUI.buttonWindow.header:setStyleSheet(GUI.DetachableHeaderCSS:getCSS())
  GUI.buttonWindow.header:echo("<center>Controls")
  GUI.buttonWindow.header:setToolTip("Double-click to detach/attach controls")
  
  -- Adjust button container position
  GUI.buttonWindow.buttonContainer.y = 20
  GUI.buttonWindow.buttonContainer.height = "100%-20"
  
  -- Make button window detachable
  GUI.buttonWindow.detachable = LUM.DetachableWindow:new(
    GUI.buttonWindow.container, 
    "ButtonWindow"
  )
  
  -- ... rest of existing code ...
end
```

### Phase 3: Integration with Existing Windows

#### Task 3.1: Update Window Initialization Order
**File:** `LuminariGUI.xml` - Modify main initialization
**Priority:** HIGH

```lua
-- Add to main GUI initialization (after existing init calls):
function GUI.init()
  -- ... existing initialization ...
  
  -- Initialize data persistence first
  LUM.data:load()
  
  -- Initialize detachable windows after all containers are created
  tempTimer(1, function()
    GUI.initDetachableWindows()
  end)
end

function GUI.initDetachableWindows()
  -- Restore all detached window states
  if GUI.tabbedInfoWindow and GUI.tabbedInfoWindow.detachable then
    -- Already handled in tabbedInfoWindow.init()
  end
  
  if GUI.chatDetachable then
    -- Already handled in init_boxes()
  end
  
  if GUI.buttonWindow and GUI.buttonWindow.detachable then
    -- Already handled in buttonWindow.init()
  end
  
  cecho("<cyan>Detachable window system initialized.\n")
end
```

#### Task 3.2: Add Detachment Commands
**File:** `LuminariGUI.xml` - New Alias Group "Window Management"
**Priority:** LOW

```lua
-- Alias: ^detach (\w+)$
-- Pattern: detach chat|detach info|detach buttons

if matches[2] == "chat" and GUI.chatDetachable then
  GUI.chatDetachable:detach()
elseif matches[2] == "info" and GUI.tabbedInfoWindow.detachable then
  GUI.tabbedInfoWindow.detachable:detach()
elseif matches[2] == "buttons" and GUI.buttonWindow.detachable then
  GUI.buttonWindow.detachable:detach()
else
  cecho("<red>Unknown window: " .. matches[2] .. "\n")
  cecho("<white>Available: chat, info, buttons\n")
end

-- Alias: ^attach (\w+)$
-- Similar implementation for reattaching windows

-- Alias: ^windows$
-- List all detachable windows and their current state
cecho("<cyan>Detachable Windows:\n")
if GUI.chatDetachable then
  local state = GUI.chatDetachable.isDetached and "detached" or "attached"
  cecho("  Chat: " .. state .. "\n")
end
if GUI.tabbedInfoWindow.detachable then
  local state = GUI.tabbedInfoWindow.detachable.isDetached and "detached" or "attached"  
  cecho("  Info: " .. state .. "\n")
end
if GUI.buttonWindow.detachable then
  local state = GUI.buttonWindow.detachable.isDetached and "detached" or "attached"
  cecho("  Buttons: " .. state .. "\n")
end
```

### Phase 4: Polish & Testing

#### Task 4.1: Add Error Handling
**File:** `LuminariGUI.xml` - Enhance DetachableWindow class
**Priority:** MEDIUM

```lua
-- Add to LUM.DetachableWindow:detach()
function LUM.DetachableWindow:detach()
  if self.isDetached then return end
  
  -- Validate container still exists
  if not self.container or not self.container.name then
    cecho("<red>Error: Container no longer exists for " .. self.name .. "\n")
    return
  end
  
  -- Check if UserWindow creation is supported
  local ok, userWindow = pcall(function()
    return Geyser.UserWindow:new({
      name = self.name .. "_detached",
      x = self.originalGeometry.x,
      y = self.originalGeometry.y, 
      width = self.originalGeometry.width,
      height = self.originalGeometry.height
    })
  end)
  
  if not ok then
    cecho("<red>Error: Failed to create detached window for " .. self.name .. "\n")
    cecho("<red>Your Mudlet version may not support UserWindows.\n")
    return
  end
  
  self.userWindow = userWindow
  -- ... rest of detach logic ...
end
```

#### Task 4.2: Add Visual Feedback
**File:** `LuminariGUI.xml` - Enhance header styling
**Priority:** LOW

```lua
-- Enhanced header CSS with hover effects
GUI.DetachableHeaderCSS = CSSMan.new([[
  background-color: rgba(60,60,60,255);
  border: 1px solid rgb(140,140,140);
  color: white;
  font-family: Tahoma, Geneva, sans-serif;
  qproperty-wordWrap: true;
]])

GUI.DetachableHeaderHoverCSS = CSSMan.new([[
  background-color: rgba(80,80,80,255);
  border: 1px solid rgb(160,160,160);
  color: yellow;
  font-family: Tahoma, Geneva, sans-serif;
  qproperty-wordWrap: true;
]])

-- Add hover effects to headers
function addDetachableHeader(container, title)
  local header = Geyser.Label:new({
    name = container.name .. "_header",
    x = 0, y = 0, width = "100%", height = 25
  }, container)
  
  header:setStyleSheet(GUI.DetachableHeaderCSS:getCSS())
  header:echo("<center>" .. title .. " - Double-click to detach")
  header:setToolTip("Double-click to detach/attach window")
  
  -- Add hover effects
  header:setEnterCallback(function()
    header:setStyleSheet(GUI.DetachableHeaderHoverCSS:getCSS())
  end)
  
  header:setLeaveCallback(function()
    header:setStyleSheet(GUI.DetachableHeaderCSS:getCSS())
  end)
  
  return header
end
```

### Implementation Checklist

#### Core Infrastructure
- [ ] Add LUM.data persistence system
- [ ] Create LUM.DetachableWindow base class
- [ ] Add window state restoration on startup

#### Window Integration
- [ ] Make chat window detachable with header
- [ ] Make info window detachable
- [ ] Make button window detachable
- [ ] Update demonnic.chat container references

#### User Experience
- [ ] Add detach/attach aliases
- [ ] Add visual header styling with hover effects
- [ ] Add tooltips and user feedback
- [ ] Add error handling for unsupported Mudlet versions

#### Testing
- [ ] Test detachment/attachment cycles
- [ ] Test state persistence across sessions
- [ ] Test with different screen resolutions
- [ ] Test error cases (missing windows, invalid states)

### Compatibility Notes

- **Minimum Mudlet Version:** 4.0+ (for UserWindow support)
- **Dependencies:** Existing Geyser framework in LuminariGUI
- **Storage:** Uses Mudlet home directory for persistence
- **Performance:** Minimal impact, state changes only on user action

### Benefits

1. **Multi-monitor Support:** Players can move panels to secondary screens
2. **Flexible Layout:** Customize GUI arrangement per player preference  
3. **Persistent Settings:** Window states saved across sessions
4. **Professional Feel:** Modern application-like window management
5. **Backwards Compatible:** Non-intrusive, works with existing GUI

This implementation provides a robust foundation for detachable windows while maintaining LuminariGUI's clean architecture and performance characteristics.

