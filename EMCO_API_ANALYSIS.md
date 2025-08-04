# EMCO API Analysis and Compatibility Requirements

## Overview
This document analyzes EMCO's API structure and identifies compatibility requirements for migrating from YATCO.

## EMCO Architecture

### 1. Object Creation
EMCO uses an object-oriented approach with Geyser inheritance:
```lua
-- EMCO inherits from Geyser.Container
local EMCO = Geyser.Container:new({name = "TabbedConsoleClass", ...})

-- Creation requires parent container
local emcoInstance = EMCO:new(constraints, parentContainer)
```

### 2. Core Methods

#### Append Methods
- `EMCO:append(tabName, excludeAll)` - Appends current line from MUD
- `EMCO:echo(tabName, message, excludeAll)` - Plain text echo
- `EMCO:cecho(tabName, message, excludeAll)` - Color echo
- `EMCO:decho(tabName, message, excludeAll)` - Decimal color echo
- `EMCO:hecho(tabName, message, excludeAll)` - Hex color echo

#### Tab Management
- `EMCO:addTab(tabName)` - Add new tab
- `EMCO:removeTab(tabName)` - Remove tab
- `EMCO:switchTab(tabName)` - Switch active tab
- `EMCO:showTab(tabName)` - Show specific tab
- `EMCO:hideTab(tabName)` - Hide specific tab

#### Configuration
- `EMCO:setTabFont(fontName)` - Set tab font
- `EMCO:setTabFontSize(size)` - Set tab font size
- `EMCO:setActiveTabFGColor(color)` - Active tab text color
- `EMCO:setInactiveTabFGColor(color)` - Inactive tab text color
- `EMCO:setConsoleColor(color)` - Console background color

### 3. Properties
EMCO stores configuration as object properties:
```lua
emcoInstance.timestamp = true
emcoInstance.blankLine = true
emcoInstance.blink = true
emcoInstance.fontSize = 12
emcoInstance.consoles = {"All", "Tell", "Chat", ...}
emcoInstance.currentTab = "All"
```

### 4. Internal Structure
```lua
-- Tab objects
emcoInstance.tabs[tabName] -- Geyser.Label for tab
emcoInstance.mc[tabName] -- MiniConsole or LoggingConsole for content
emcoInstance.tabsToBlink -- Table of tabs that should blink
```

## Key Differences from YATCO

### 1. API Style
- **YATCO**: Global object with config namespace
  ```lua
  demonnic.chat:append("Tell")
  demonnic.chat.config.blink = true
  ```
- **EMCO**: Instance methods and properties
  ```lua
  emcoInstance:append("Tell")
  emcoInstance.blink = true
  ```

### 2. Window Access
- **YATCO**: `demonnic.chat.windows[tabName]`
- **EMCO**: `emcoInstance.mc[tabName]`

### 3. Tab Access
- **YATCO**: `demonnic.chat.tabs[tabName]`
- **EMCO**: `emcoInstance.tabs[tabName]`

### 4. Configuration
- **YATCO**: Nested config object `demonnic.chat.config.*`
- **EMCO**: Direct properties on instance

### 5. Container Assignment
- **YATCO**: `demonnic.chat.useContainer = container`
- **EMCO**: Pass container to constructor

## Compatibility Requirements

### 1. Global Object Mapping
Create `demonnic.chat` as a wrapper around EMCO instance:
```lua
demonnic.chat = {
  -- Forward method calls to EMCO instance
  append = function(self, tabName)
    return emcoInstance:append(tabName)
  end,
  
  -- Map config namespace to EMCO properties
  config = setmetatable({}, {
    __index = function(t, k)
      return emcoInstance[k]
    end,
    __newindex = function(t, k, v)
      emcoInstance[k] = v
    end
  })
}
```

### 2. Window/Tab Compatibility
Map YATCO's window/tab access:
```lua
demonnic.chat.windows = setmetatable({}, {
  __index = function(t, k)
    return emcoInstance.mc[k]
  end
})

demonnic.chat.tabs = setmetatable({}, {
  __index = function(t, k)
    return emcoInstance.tabs[k]
  end
})
```

### 3. Function Compatibility
Implement missing YATCO functions:
- `demonnic.chat:create()` - Initialize EMCO
- `demonnic.chat:resetUI()` - Call EMCO:reset()
- `demonnic.chat:showAllTabs()` - Show all tabs
- `demonnic.chat:blink()` - Start blink timer

### 4. Event Compatibility
Map YATCO events to EMCO:
- Tab switch callbacks
- Blink timer management
- Sound notification hooks

### 5. Configuration Mapping
Map all YATCO config options to EMCO equivalents:
- `demonnic.chat.config.timestamp` → `emco.timestamp`
- `demonnic.chat.config.blink` → `emco.blink`
- `demonnic.chat.config.fontSize` → `emco.fontSize`
- `demonnic.chat.config.channels` → `emco.consoles`
- `demonnic.chat.config.Alltab` → `emco.allTabName`

## Implementation Strategy

### Phase 1: Compatibility Layer
1. Create wrapper object maintaining YATCO API
2. Map all properties and methods to EMCO
3. Implement missing functionality

### Phase 2: Integration
1. Initialize EMCO with proper container
2. Configure with existing settings
3. Verify all triggers work

### Phase 3: Testing
1. Test each chat trigger
2. Verify all aliases function
3. Check custom modifications (colors, sounds)
4. Validate Adjustable Container integration

### Phase 4: Optimization
1. Remove unnecessary wrapper overhead
2. Direct EMCO usage where possible
3. Performance testing

## Critical Success Factors
1. Zero changes required to existing triggers
2. All aliases continue to work
3. User experience remains identical
4. No loss of functionality
5. Improved performance/features from EMCO