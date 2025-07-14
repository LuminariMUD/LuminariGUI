
## Advanced Window Management Implementation Plan

### Overview
Add detachable window functionality to LuminariGUI using proper integration with the existing architecture, dependency management system, and established coding patterns. This will allow players to detach GUI panels into separate windows for multi-monitor setups while maintaining full compatibility with the existing system.

### Architecture Integration Analysis

#### Current LuminariGUI Structure
- **Primary Namespace**: `GUI.` (not LUM.)
- **Dependency System**: `GUI.DependencyManager` with comprehensive initialization ordering
- **Error Handling**: `GUI.createErrorBoundary` and resource cleanup systems
- **State Management**: `GUI.StateManager` with schema validation and persistence
- **Chat Integration**: `demonnic.chat.useContainer = GUI.chatContainer` (already properly integrated)
- **Component Structure**: Well-defined component hierarchy with proper parent-child relationships

#### Existing Window Components
1. **Tabbed Info Window**: `GUI.tabbedInfoWindow.container` (contains Player, Affects, Group tabs)
2. **Chat System**: `GUI.chatContainer` (contains YATCO chat with tabs)
3. **Button Window**: `GUI.buttonWindow.container` (contains navigation controls)
4. **Map Display**: `GUI.Box5` (contains room info and map legend)
5. **Status Gauges**: `GUI.Box7` (contains health, movement, experience gauges)

### Phase 1: Core Infrastructure

#### Task 1.1: Extend Existing State Management System
**File:** `LuminariGUI.xml` - Extend "Config" script
**Priority:** HIGH

```lua
-- Extend existing GUI.StateManager schema for window detachment states
GUI.StateManager.schema.windows = {
  default = {
    detached = {},
    positions = {},
    sizes = {}
  },
  validator = function(value)
    return type(value) == "table" and type(value.detached) == "table"
  end,
  sanitizer = function(value)
    if type(value) ~= "table" then
      return { detached = {}, positions = {}, sizes = {} }
    end
    return {
      detached = type(value.detached) == "table" and value.detached or {},
      positions = type(value.positions) == "table" and value.positions or {},
      sizes = type(value.sizes) == "table" and value.sizes or {}
    }
  end
}

-- Add window state persistence functions
function GUI.getWindowState(windowName)
  local state = GUI.StateManager:get("windows", {})
  return {
    detached = state.detached[windowName] or false,
    position = state.positions[windowName] or { x = 100, y = 100 },
    size = state.sizes[windowName] or { width = 400, height = 300 }
  }
end

function GUI.setWindowState(windowName, detached, position, size)
  local state = GUI.StateManager:get("windows", {})
  state.detached[windowName] = detached
  if position then state.positions[windowName] = position end
  if size then state.sizes[windowName] = size end
  GUI.StateManager:set("windows", state)
end
```

#### Task 1.2: Create Detachable Window System
**File:** `LuminariGUI.xml` - New Script "DetachableWindow"
**Priority:** HIGH

```lua
-- Detachable window manager using proper GUI namespace
GUI.DetachableWindow = GUI.DetachableWindow or {}

function GUI.DetachableWindow:new(config)
  if not config or not config.container or not config.name then
    cecho("<red>[DetachableWindow] Invalid configuration - container and name required\n")
    return nil
  end
  
  local obj = {
    container = config.container,
    name = config.name,
    title = config.title or config.name,
    isDetached = false,
    userWindow = nil,
    originalParent = config.container.parent,
    originalConstraints = {},
    headerHeight = config.headerHeight or 25,
    onDetach = config.onDetach,
    onAttach = config.onAttach,
    minWidth = config.minWidth or 300,
    minHeight = config.minHeight or 200
  }
  setmetatable(obj, {__index = self})
  
  -- Store original constraints
  obj.originalConstraints = {
    x = obj.container.x,
    y = obj.container.y,
    width = obj.container.width,
    height = obj.container.height
  }
  
  -- Create detachable header
  obj:createHeader()
  
  -- Restore previous state if exists
  local windowState = GUI.getWindowState(obj.name)
  if windowState.detached then
    -- Defer detachment to after full initialization
    GUI.registerTimer(100, function()
      obj:detach(windowState.position, windowState.size)
    end, false, "detach_restore_" .. obj.name)
  end
  
  return obj
end

function GUI.DetachableWindow:createHeader()
  -- Create header container
  self.header = Geyser.Label:new({
    name = self.name .. "_detach_header",
    x = 0, y = 0,
    width = "100%", height = self.headerHeight
  }, self.container)
  
  -- Style header
  self.header:setStyleSheet([[
    background-color: rgba(70,70,70,255);
    border: 1px solid rgb(150,150,150);
    color: white;
    font-family: Tahoma, Geneva, sans-serif;
    font-size: 11px;
    font-weight: bold;
    qproperty-wordWrap: true;
  ]])
  
  -- Header content
  self.header:echo("<center>" .. self.title .. " - Double-click to detach</center>")
  self.header:setToolTip("Double-click to detach/attach this window")
  
  -- Add double-click handler
  self.header:setDoubleClickCallback(function()
    GUI.createErrorBoundary("detach_toggle_" .. self.name, function()
      self:toggle()
    end)()
  end)
  
  -- Add hover effects
  self.header:setEnterCallback(function()
    self.header:setStyleSheet([[
      background-color: rgba(90,90,90,255);
      border: 1px solid rgb(170,170,170);
      color: yellow;
      font-family: Tahoma, Geneva, sans-serif;
      font-size: 11px;
      font-weight: bold;
      qproperty-wordWrap: true;
    ]])
  end)
  
  self.header:setLeaveCallback(function()
    self.header:setStyleSheet([[
      background-color: rgba(70,70,70,255);
      border: 1px solid rgb(150,150,150);
      color: white;
      font-family: Tahoma, Geneva, sans-serif;
      font-size: 11px;
      font-weight: bold;
      qproperty-wordWrap: true;
    ]])
  end)
  
  -- Adjust container content to account for header
  self:adjustContentArea()
end

function GUI.DetachableWindow:adjustContentArea()
  -- Find all child elements and adjust their positions
  for name, child in pairs(self.container.children or {}) do
    if child ~= self.header then
      -- Adjust Y position to account for header
      local currentY = child.y
      if type(currentY) == "number" then
        child.y = currentY + self.headerHeight
      elseif type(currentY) == "string" and not currentY:match("%%") then
        child.y = tostring(tonumber(currentY) + self.headerHeight)
      end
      
      -- Adjust height to account for header
      local currentHeight = child.height
      if type(currentHeight) == "string" and currentHeight:match("%%") then
        local percentage = tonumber(currentHeight:match("(%d+)%%"))
        if percentage then
          child.height = tostring(percentage) .. "%-" .. self.headerHeight
        end
      elseif type(currentHeight) == "number" then
        child.height = currentHeight - self.headerHeight
      end
    end
  end
end

function GUI.DetachableWindow:toggle()
  if self.isDetached then
    self:attach()
  else
    self:detach()
  end
end

function GUI.DetachableWindow:detach(position, size)
  if self.isDetached then 
    cecho("<yellow>[DetachableWindow] " .. self.name .. " is already detached\n")
    return false
  end
  
  -- Validate UserWindow support
  if not Geyser.UserWindow then
    cecho("<red>[DetachableWindow] UserWindow not supported in this Mudlet version\n")
    return false
  end
  
  -- Get current container dimensions
  local containerWidth = self.container:get_width()
  local containerHeight = self.container:get_height()
  
  -- Use provided size or calculate from current container
  local windowSize = size or {
    width = math.max(containerWidth, self.minWidth),
    height = math.max(containerHeight, self.minHeight)
  }
  
  -- Use provided position or calculate default
  local windowPosition = position or {
    x = 100,
    y = 100
  }
  
  -- Create user window with error handling
  local success, userWindow = pcall(function()
    return Geyser.UserWindow:new({
      name = self.name .. "_detached_window",
      x = windowPosition.x,
      y = windowPosition.y,
      width = windowSize.width,
      height = windowSize.height,
      titleText = self.title
    })
  end)
  
  if not success then
    cecho("<red>[DetachableWindow] Failed to create user window: " .. tostring(userWindow) .. "\n")
    return false
  end
  
  self.userWindow = userWindow
  
  -- Move container to user window
  self.container:changeContainer(self.userWindow)
  self.container:resize("100%", "100%")
  self.container:move(0, 0)
  
  -- Update state
  self.isDetached = true
  GUI.setWindowState(self.name, true, windowPosition, windowSize)
  
  -- Update header text
  self.header:echo("<center>" .. self.title .. " - Double-click to reattach</center>")
  
  -- Call custom detach callback if provided
  if self.onDetach and type(self.onDetach) == "function" then
    pcall(self.onDetach, self)
  end
  
  cecho("<green>[DetachableWindow] " .. self.name .. " detached successfully\n")
  return true
end

function GUI.DetachableWindow:attach()
  if not self.isDetached then
    cecho("<yellow>[DetachableWindow] " .. self.name .. " is already attached\n")
    return false
  end
  
  -- Store current window position/size before destroying
  if self.userWindow then
    local windowPos = {
      x = self.userWindow:get_x(),
      y = self.userWindow:get_y()
    }
    local windowSize = {
      width = self.userWindow:get_width(),
      height = self.userWindow:get_height()
    }
    GUI.setWindowState(self.name, false, windowPos, windowSize)
    
    -- Hide and destroy user window
    self.userWindow:hide()
    self.userWindow = nil
  end
  
  -- Move container back to original parent
  self.container:changeContainer(self.originalParent)
  self.container:resize(self.originalConstraints.width, self.originalConstraints.height)
  self.container:move(self.originalConstraints.x, self.originalConstraints.y)
  
  -- Update state
  self.isDetached = false
  
  -- Update header text
  self.header:echo("<center>" .. self.title .. " - Double-click to detach</center>")
  
  -- Call custom attach callback if provided
  if self.onAttach and type(self.onAttach) == "function" then
    pcall(self.onAttach, self)
  end
  
  cecho("<green>[DetachableWindow] " .. self.name .. " reattached successfully\n")
  return true
end

function GUI.DetachableWindow:destroy()
  if self.isDetached and self.userWindow then
    self.userWindow:hide()
    self.userWindow = nil
  end
  
  if self.header then
    self.header:hide()
    self.header = nil
  end
  
  -- Clean up state
  GUI.setWindowState(self.name, false, nil, nil)
end
```

### Phase 2: Window Integration

#### Task 2.1: Integrate with Dependency System
**File:** `LuminariGUI.xml` - Modify "Config" script's `GUI.initializeDependencies()`
**Priority:** HIGH

```lua
-- Add detachable window initialization to existing dependency system
function GUI.initializeDependencies()
  local dm = GUI.DependencyManager
  cecho("<cyan>[Init] Registering component dependencies...\n")
  
  -- ... existing registrations ...
  
  -- Add detachable window system after all UI components are ready
  dm:register("detachable_windows", {"tabbed_info", "cast_console", "button_window"}, function()
    GUI.initDetachableWindows()
  end)
  
  cecho("<green>[Init] Component dependencies registered\n")
end

function GUI.initDetachableWindows()
  cecho("<cyan>[Init] Initializing detachable window system...\n")
  
  -- Initialize detachable windows for major components
  GUI.detachableWindows = {}
  
  -- Tabbed Info Window (Player, Affects, Group tabs)
  if GUI.tabbedInfoWindow and GUI.tabbedInfoWindow.container then
    GUI.detachableWindows.info = GUI.DetachableWindow:new({
      container = GUI.tabbedInfoWindow.container,
      name = "InfoWindow",
      title = "Character Information",
      minWidth = 350,
      minHeight = 400
    })
  end
  
  -- Cast Console Window
  if GUI.castConsole then
    GUI.detachableWindows.cast = GUI.DetachableWindow:new({
      container = GUI.castConsole,
      name = "CastConsole",
      title = "Spell Casting",
      minWidth = 300,
      minHeight = 150
    })
  end
  
  -- Button Window (Navigation Controls)
  if GUI.buttonWindow and GUI.buttonWindow.container then
    GUI.detachableWindows.buttons = GUI.DetachableWindow:new({
      container = GUI.buttonWindow.container,
      name = "ButtonWindow",
      title = "Navigation Controls",
      minWidth = 200,
      minHeight = 100
    })
  end
  
  -- Map/Room Info Window
  if GUI.Box5 then
    -- Create a wrapper container for the map area
    GUI.mapContainer = Geyser.Container:new({
      name = "GUI.mapContainer",
      x = 0, y = 0,
      width = "100%", height = "100%"
    }, GUI.Box5)
    
    -- Move existing map content to wrapper
    if GUI.buttonWindow and GUI.buttonWindow.roomInfo then
      GUI.buttonWindow.roomInfo:changeContainer(GUI.mapContainer)
    end
    if GUI.buttonWindow and GUI.buttonWindow.Legend then
      GUI.buttonWindow.Legend:changeContainer(GUI.mapContainer)
    end
    
    GUI.detachableWindows.map = GUI.DetachableWindow:new({
      container = GUI.mapContainer,
      name = "MapWindow",
      title = "Map & Room Info",
      minWidth = 300,
      minHeight = 200
    })
  end
  
  cecho("<green>[Init] Detachable window system initialized\n")
end
```

#### Task 2.2: Add User Commands
**File:** `LuminariGUI.xml` - New Alias Group "WindowManagement"
**Priority:** MEDIUM

```lua
-- Alias Pattern: ^detach (\w+)$
-- Detach specific window
local windowName = matches[2]:lower()
local windowMap = {
  info = "info",
  character = "info",
  player = "info",
  affects = "info",
  group = "info",
  cast = "cast",
  casting = "cast",
  spell = "cast",
  buttons = "buttons",
  navigation = "buttons",
  controls = "buttons",
  map = "map",
  room = "map",
  legend = "map"
}

local targetWindow = windowMap[windowName]
if targetWindow and GUI.detachableWindows[targetWindow] then
  GUI.detachableWindows[targetWindow]:detach()
else
  cecho("<red>Unknown window: " .. windowName .. "\n")
  cecho("<white>Available windows: info, cast, buttons, map\n")
end

-- Alias Pattern: ^attach (\w+)$
-- Attach specific window
local windowName = matches[2]:lower()
local windowMap = {
  info = "info",
  character = "info",
  player = "info",
  affects = "info",
  group = "info",
  cast = "cast",
  casting = "cast",
  spell = "cast",
  buttons = "buttons",
  navigation = "buttons",
  controls = "buttons",
  map = "map",
  room = "map",
  legend = "map"
}

local targetWindow = windowMap[windowName]
if targetWindow and GUI.detachableWindows[targetWindow] then
  GUI.detachableWindows[targetWindow]:attach()
else
  cecho("<red>Unknown window: " .. windowName .. "\n")
  cecho("<white>Available windows: info, cast, buttons, map\n")
end

-- Alias Pattern: ^windows$
-- List all detachable windows and their states
cecho("<cyan>Detachable Windows Status:\n")
if GUI.detachableWindows then
  for name, window in pairs(GUI.detachableWindows) do
    local state = window.isDetached and "<green>detached" or "<yellow>attached"
    cecho(string.format("  %s: %s\n", name, state))
  end
else
  cecho("<red>Detachable window system not initialized\n")
end

-- Alias Pattern: ^detach all$
-- Detach all windows
if GUI.detachableWindows then
  for name, window in pairs(GUI.detachableWindows) do
    if not window.isDetached then
      window:detach()
    end
  end
  cecho("<green>All windows detached\n")
else
  cecho("<red>Detachable window system not initialized\n")
end

-- Alias Pattern: ^attach all$
-- Attach all windows
if GUI.detachableWindows then
  for name, window in pairs(GUI.detachableWindows) do
    if window.isDetached then
      window:attach()
    end
  end
  cecho("<green>All windows attached\n")
else
  cecho("<red>Detachable window system not initialized\n")
end
```

### Phase 3: Enhanced Features

#### Task 3.1: Add Chat Window Integration
**File:** `LuminariGUI.xml` - Modify existing chat container setup
**Priority:** LOW

```lua
-- Add to existing chat initialization (after demonnic.chat:create())
function GUI.initChatDetachment()
  if GUI.chatContainer and demonnic.chat.container then
    GUI.detachableWindows.chat = GUI.DetachableWindow:new({
      container = GUI.chatContainer,
      name = "ChatWindow",
      title = "Chat System",
      minWidth = 400,
      minHeight = 300,
      onDetach = function(self)
        -- Adjust chat container sizing when detached
        if demonnic.chat.container then
          demonnic.chat.container:resize("100%", "100%-" .. self.headerHeight)
          demonnic.chat.container:move(0, self.headerHeight)
        end
      end,
      onAttach = function(self)
        -- Restore chat container sizing when attached
        if demonnic.chat.container then
          demonnic.chat.container:resize("100%", "100%")
          demonnic.chat.container:move(0, 0)
        end
      end
    })
  end
end

-- Add to dependency registration
dm:register("chat_detachment", {"detachable_windows"}, function()
  GUI.initChatDetachment()
end)
```

#### Task 3.2: Add Status Gauge Window
**File:** `LuminariGUI.xml` - Create gauge window wrapper
**Priority:** LOW

```lua
function GUI.initGaugeDetachment()
  if GUI.Box7 then
    -- Create wrapper for gauge area
    GUI.gaugeContainer = Geyser.Container:new({
      name = "GUI.gaugeContainer",
      x = 0, y = 0,
      width = "100%", height = "100%"
    }, GUI.Box7)
    
    -- Move existing gauges to wrapper
    local gaugeComponents = {
      "GaugeBar", "Health", "Moves", "Experience", "EnemyGauge", 
      "StandardActionIcon", "MoveActionIcon", "SwiftActionIcon"
    }
    
    for _, componentName in ipairs(gaugeComponents) do
      if GUI[componentName] then
        GUI[componentName]:changeContainer(GUI.gaugeContainer)
      end
    end
    
    GUI.detachableWindows.gauges = GUI.DetachableWindow:new({
      container = GUI.gaugeContainer,
      name = "GaugeWindow",
      title = "Status Gauges",
      minWidth = 300,
      minHeight = 150
    })
  end
end

-- Add to dependency registration
dm:register("gauge_detachment", {"detachable_windows"}, function()
  GUI.initGaugeDetachment()
end)
```

### Phase 4: Testing and Validation

#### Task 4.1: Add Comprehensive Error Handling
**File:** `LuminariGUI.xml` - Enhance error handling
**Priority:** HIGH

```lua
-- Add detachable window validation to existing system
function GUI.validateDetachableWindows()
  if not GUI.detachableWindows then
    cecho("<red>[Validation] Detachable windows not initialized\n")
    return false
  end
  
  local validationErrors = {}
  
  for name, window in pairs(GUI.detachableWindows) do
    if not window.container then
      table.insert(validationErrors, "Window " .. name .. " has no container")
    end
    
    if not window.header then
      table.insert(validationErrors, "Window " .. name .. " has no header")
    end
    
    if window.isDetached and not window.userWindow then
      table.insert(validationErrors, "Window " .. name .. " claims to be detached but has no UserWindow")
    end
  end
  
  if #validationErrors > 0 then
    cecho("<red>[Validation] Detachable window validation failed:\n")
    for _, error in ipairs(validationErrors) do
      cecho("<red>  - " .. error .. "\n")
    end
    return false
  end
  
  cecho("<green>[Validation] All detachable windows valid\n")
  return true
end

-- Add to existing validation system
function GUI.validateInitialization()
  -- ... existing validation code ...
  
  -- Add detachable window validation
  if not GUI.validateDetachableWindows() then
    table.insert(validationErrors, "Detachable window system validation failed")
  end
  
  -- ... rest of existing validation ...
end
```

#### Task 4.2: Add Cleanup Integration
**File:** `LuminariGUI.xml` - Integrate with resource cleanup
**Priority:** MEDIUM

```lua
-- Add to existing cleanup system
function GUI.cleanupDetachableWindows()
  if GUI.detachableWindows then
    for name, window in pairs(GUI.detachableWindows) do
      if window.destroy then
        window:destroy()
      end
    end
    GUI.detachableWindows = nil
  end
end

-- Integrate with existing cleanup handlers
registerAnonymousEventHandler("sysUninstall", GUI.createErrorBoundary("detach_cleanup_uninstall", function()
  GUI.cleanupDetachableWindows()
end))

registerAnonymousEventHandler("sysExitEvent", GUI.createErrorBoundary("detach_cleanup_exit", function()
  GUI.cleanupDetachableWindows()
end))
```

### Implementation Checklist

#### Core Infrastructure (Phase 1)
- [ ] Extend existing `GUI.StateManager` schema for window states
- [ ] Create `GUI.DetachableWindow` class with proper error handling
- [ ] Integrate with existing `GUI.DependencyManager` system
- [ ] Add window state persistence using existing mechanisms

#### Window Integration (Phase 2)
- [ ] Create detachable wrappers for all major UI components
- [ ] Integrate with existing initialization system
- [ ] Add user command aliases for window management
- [ ] Implement proper parent-child container relationships

#### Enhanced Features (Phase 3)
- [ ] Add chat window detachment with YATCO integration
- [ ] Create gauge window wrapper with proper component migration
- [ ] Implement custom callbacks for specialized window behavior
- [ ] Add visual feedback and hover effects

#### Testing and Validation (Phase 4)
- [ ] Integrate with existing validation framework
- [ ] Add comprehensive error handling using existing patterns
- [ ] Implement resource cleanup integration
- [ ] Add debugging and monitoring capabilities

### Compatibility Requirements

- **Minimum Mudlet Version:** 4.0+ (for `Geyser.UserWindow` support)
- **Dependencies:** Existing LuminariGUI architecture (no additional dependencies)
- **Storage:** Uses existing `GUI.StateManager` for persistence
- **Performance:** Minimal impact using existing error boundary system

### Benefits

1. **Seamless Integration**: Works with existing dependency management and initialization
2. **Multi-monitor Support**: Professional window management for enhanced workflows
3. **Persistent State**: Window positions and states saved automatically
4. **Error Resilience**: Full integration with existing error handling infrastructure
5. **Backwards Compatible**: Graceful degradation when UserWindow unsupported
6. **Extensible**: Easy to add new detachable windows using established patterns

This implementation provides a robust, production-ready detachable window system that integrates seamlessly with LuminariGUI's existing architecture while maintaining all current functionality and stability guarantees.

