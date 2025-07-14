# LuminariGUI API Documentation

This document provides comprehensive API documentation for developers working with or extending LuminariGUI. All functions and examples are based on Lua and the Mudlet client framework.

## Table of Contents

- [Core GUI API](#core-gui-api)
- [MSDP Integration API](#msdp-integration-api)
- [Component APIs](#component-apis)
- [Configuration API](#configuration-api)
- [Event System](#event-system)
- [Extension Points](#extension-points)
- [Code Examples](#code-examples)

## Core GUI API

### Initialization Functions

#### `GUI.init()`
Initializes the complete LuminariGUI system.

```lua
-- Initialize the entire GUI system
GUI.init()
```

**Called by**: System startup, package installation
**Dependencies**: Mudlet, Geyser framework
**Side effects**: Creates all GUI components, registers event handlers

#### `GUI.init_background()`
Creates the base layout structure and background styling.

```lua
-- Initialize background layout
GUI.init_background()
```

**Components created**:
- `GUI.Root`: Main container
- `GUI.Left`: Left panel (character info)
- `GUI.Right`: Right panel (map/controls)
- `GUI.Bottom`: Bottom panel (chat/status)

#### `GUI.init_boxes()`
Initializes the main content containers within the layout.

```lua
-- Create content boxes
GUI.init_boxes()
```

**Components created**:
- `GUI.Box2`: Chat container
- `GUI.Box3`: Control buttons
- `GUI.Box4`: Tabbed info window
- `GUI.Box5`: Map display area
- `GUI.Box7`: Status gauges

#### `GUI.init_gauges()`
Creates all status gauge components.

```lua
-- Initialize status gauges
GUI.init_gauges()
```

**Components created**:
- `GUI.HealthGauge`: Health display
- `GUI.MovesGauge`: Movement points
- `GUI.ExperienceGauge`: Experience progress
- `GUI.EnemyGauge`: Enemy health (when in combat)

### Update Functions

#### `GUI.updateHealthGauge()`
Updates the health gauge display based on MSDP data.

```lua
function GUI.updateHealthGauge()
    if not msdp.HEALTH or not msdp.MAX_HEALTH then return end
    
    local current = tonumber(msdp.HEALTH)
    local maximum = tonumber(msdp.MAX_HEALTH)
    local percentage = (current / maximum) * 100
    
    GUI.HealthGauge:setValue(current, maximum)
    GUI.HealthGauge:setToolTip(string.format("Health: %d/%d (%.1f%%)", 
                                           current, maximum, percentage))
end
```

#### `GUI.updateMovesGauge()`
Updates the movement points gauge.

```lua
function GUI.updateMovesGauge()
    if not msdp.MOVEMENT or not msdp.MAX_MOVEMENT then return end
    
    local current = tonumber(msdp.MOVEMENT)
    local maximum = tonumber(msdp.MAX_MOVEMENT)
    
    GUI.MovesGauge:setValue(current, maximum)
    GUI.MovesGauge:setToolTip(string.format("Movement: %d/%d", current, maximum))
end
```

#### `GUI.updateExperienceGauge()`
Updates the experience progress display.

```lua
function GUI.updateExperienceGauge()
    if not msdp.EXPERIENCE then return end
    
    local current = tonumber(msdp.EXPERIENCE)
    local tnl = tonumber(msdp.EXPERIENCE_TNL) or 0
    local maximum = current + tnl
    
    GUI.ExperienceGauge:setValue(current, maximum)
    GUI.ExperienceGauge:setToolTip(string.format("Experience: %d (TNL: %d)", 
                                                current, tnl))
end
```

### Utility Functions

#### `GUI.getButtonHtml(text, command, style)`
Generates HTML for clickable buttons.

```lua
-- Create a styled button
local buttonHtml = GUI.getButtonHtml("Cast Fireball", "cast fireball", "spell-button")

-- Parameters:
-- text: Display text for the button
-- command: Mudlet command to execute on click
-- style: CSS class for styling (optional)
```

#### `GUI.toggleVisibility(component)`
Toggles the visibility of a GUI component.

```lua
-- Toggle map visibility
GUI.toggleVisibility(GUI.Box5)

-- Toggle chat visibility
GUI.toggleVisibility(GUI.Box2)
```

## MSDP Integration API

### Event Registration

LuminariGUI registers handlers for various MSDP variables. Here's how to work with them:

```lua
-- Register a new MSDP handler
registerAnonymousEventHandler("msdp.VARIABLE_NAME", "handlerFunction")

-- Example: Custom health handler
function customHealthHandler()
    print("Health changed to: " .. msdp.HEALTH)
end

registerAnonymousEventHandler("msdp.HEALTH", "customHealthHandler")
```

### Core MSDP Variables

#### Character Stats
- `msdp.HEALTH`: Current health points
- `msdp.MAX_HEALTH`: Maximum health points
- `msdp.MOVEMENT`: Current movement points
- `msdp.MAX_MOVEMENT`: Maximum movement points
- `msdp.EXPERIENCE`: Current experience points
- `msdp.EXPERIENCE_TNL`: Experience to next level

#### Combat Data
- `msdp.OPPONENT_HEALTH`: Enemy health percentage
- `msdp.OPPONENT_NAME`: Current target name
- `msdp.ACTIONS`: Available actions/abilities

#### Environment
- `msdp.ROOM`: Current room information
- `msdp.ROOM_NAME`: Current room name
- `msdp.ROOM_EXITS`: Available exits
- `msdp.AREA_NAME`: Current area name

#### Social/Group
- `msdp.GROUP`: Group member information
- `msdp.AFFECTS`: Current spell effects

### MSDP Request Functions

#### `GUI.onProtocolEnabled()`
Requests initial MSDP variables when protocol is enabled.

```lua
function GUI.onProtocolEnabled()
    -- Request core character data
    sendMSDP("REQUEST", "HEALTH")
    sendMSDP("REQUEST", "MAX_HEALTH")
    sendMSDP("REQUEST", "MOVEMENT")
    sendMSDP("REQUEST", "MAX_MOVEMENT")
    
    -- Request combat data
    sendMSDP("REQUEST", "OPPONENT_HEALTH")
    sendMSDP("REQUEST", "ACTIONS")
    
    -- Request environment data
    sendMSDP("REQUEST", "ROOM")
    sendMSDP("REQUEST", "GROUP")
    sendMSDP("REQUEST", "AFFECTS")
end
```

### Custom MSDP Handlers

```lua
-- Example: Custom room handler with additional processing
function customRoomHandler()
    if not msdp.ROOM then return end
    
    local roomData = msdp.ROOM
    
    -- Process room data
    if roomData.name then
        GUI.updateRoomDisplay(roomData.name)
    end
    
    if roomData.exits then
        GUI.updateExitDisplay(roomData.exits)
    end
    
    if roomData.sector then
        GUI.updateMapSector(roomData.sector)
    end
end

registerAnonymousEventHandler("msdp.ROOM", "customRoomHandler")
```

## Component APIs

### Geyser Component Access

All GUI components are accessible through the `GUI` namespace:

```lua
-- Main containers
GUI.Root          -- Root container
GUI.Left          -- Left panel
GUI.Right         -- Right panel  
GUI.Bottom        -- Bottom panel

-- Content boxes
GUI.Box2          -- Chat container
GUI.Box3          -- Control buttons
GUI.Box4          -- Tabbed info window
GUI.Box5          -- Map display
GUI.Box7          -- Status gauges

-- Individual gauges
GUI.HealthGauge   -- Health display
GUI.MovesGauge    -- Movement points
GUI.ExperienceGauge -- Experience progress
GUI.EnemyGauge    -- Enemy health
```

### Gauge API

#### Setting Values
```lua
-- Set gauge value (current, maximum)
GUI.HealthGauge:setValue(150, 200)

-- Set gauge text
GUI.HealthGauge:setText("HP: 150/200")

-- Set tooltip
GUI.HealthGauge:setToolTip("Health: 75%")
```

#### Styling Gauges
```lua
-- Set gauge colors
GUI.HealthGauge:setColor(255, 0, 0)  -- Red foreground
GUI.HealthGauge:setBackgroundColor(50, 50, 50)  -- Dark background

-- Set gauge style
GUI.HealthGauge:setStyleSheet([[
    background-color: rgba(50, 50, 50, 200);
    border: 1px solid #888;
    border-radius: 3px;
]])
```

### Tabbed Interface API

#### `GUI.tabbedInfoWindow`
Access to the main tabbed information display.

```lua
-- Add a new tab
GUI.tabbedInfoWindow:addTab("Custom Tab", "customTabContainer")

-- Switch to a tab
GUI.tabbedInfoWindow:switchTab("Player")

-- Remove a tab
GUI.tabbedInfoWindow:removeTab("Custom Tab")
```

#### Custom Tab Creation
```lua
function createCustomTab()
    -- Create tab container
    GUI.customTab = Geyser.Container:new({
        name = "customTab",
        x = 0, y = 0,
        width = "100%", height = "100%"
    }, GUI.Box4)
    
    -- Add content
    GUI.customTabLabel = Geyser.Label:new({
        name = "customTabLabel",
        x = 5, y = 5,
        width = "100%-10", height = 20
    }, GUI.customTab)
    
    GUI.customTabLabel:echo("Custom tab content")
    
    -- Add to tabbed window
    GUI.tabbedInfoWindow:addTab("Custom", GUI.customTab)
end
```

## Configuration API

### GUI Configuration

#### Default Configuration Structure
```lua
GUI.config = {
    layout = {
        leftPanelWidth = 300,
        rightPanelWidth = 250,
        bottomPanelHeight = 200
    },
    gauges = {
        showPercentages = true,
        animateChanges = true,
        updateFrequency = 100
    },
    display = {
        showMap = true,
        showChat = true,
        showStatusGauges = true
    }
}
```

#### Configuration Functions

```lua
-- Get configuration value
function GUI.getConfig(key, default)
    local keys = string.split(key, ".")
    local value = GUI.config
    
    for _, k in ipairs(keys) do
        if value[k] then
            value = value[k]
        else
            return default
        end
    end
    
    return value
end

-- Set configuration value
function GUI.setConfig(key, value)
    local keys = string.split(key, ".")
    local config = GUI.config
    
    for i = 1, #keys - 1 do
        local k = keys[i]
        if not config[k] then
            config[k] = {}
        end
        config = config[k]
    end
    
    config[keys[#keys]] = value
    GUI.saveConfig()
end

-- Example usage
GUI.setConfig("layout.leftPanelWidth", 350)
local width = GUI.getConfig("layout.leftPanelWidth", 300)
```

### YATCO Configuration

#### Channel Configuration
```lua
demonnic.chat.config.channels = {
    chat = {
        color = "white",
        timestamp = true,
        blink = true
    },
    tell = {
        color = "cyan", 
        timestamp = true,
        blink = true,
        preserveBackground = true
    },
    group = {
        color = "yellow",
        timestamp = true,
        blink = false
    }
}
```

#### Adding Custom Channels
```lua
function addCustomChannel(name, config)
    demonnic.chat.config.channels[name] = config
    demonnic.chat:addTab(name)
end

-- Example: Add a guild channel
addCustomChannel("guild", {
    color = "green",
    timestamp = true,
    blink = true
})
```

## Event System

### Core Events

#### GUI Events
```lua
-- GUI initialization complete
raiseEvent("LuminariGUI.initialized")

-- Component visibility changed
raiseEvent("LuminariGUI.componentToggled", componentName, visible)

-- Configuration changed
raiseEvent("LuminariGUI.configChanged", key, oldValue, newValue)
```

#### Custom Event Handlers
```lua
-- Listen for GUI events
function onGUIInitialized()
    print("LuminariGUI is ready!")
    -- Perform custom initialization
end

registerAnonymousEventHandler("LuminariGUI.initialized", "onGUIInitialized")

-- Handle component toggles
function onComponentToggled(event, component, visible)
    print(string.format("Component %s is now %s", 
                       component, visible and "visible" or "hidden"))
end

registerAnonymousEventHandler("LuminariGUI.componentToggled", "onComponentToggled")
```

### MSDP Events

#### Available MSDP Events
All MSDP variables generate corresponding events:

```lua
-- Character events
"msdp.HEALTH"
"msdp.MAX_HEALTH" 
"msdp.MOVEMENT"
"msdp.MAX_MOVEMENT"
"msdp.EXPERIENCE"

-- Combat events
"msdp.OPPONENT_HEALTH"
"msdp.OPPONENT_NAME"
"msdp.ACTIONS"

-- Environment events
"msdp.ROOM"
"msdp.AREA_NAME"
"msdp.GROUP"
"msdp.AFFECTS"
```

## Extension Points

### Adding Custom GUI Components

#### 1. Create Component Initialization
```lua
function GUI.init_customComponent()
    GUI.customComponent = Geyser.Label:new({
        name = "customComponent",
        x = 10, y = 10,
        width = 200, height = 30
    }, GUI.Right)
    
    GUI.customComponent:setStyleSheet([[
        background-color: rgba(0, 0, 0, 150);
        border: 1px solid #666;
        color: white;
        font-size: 12pt;
    ]])
    
    GUI.customComponent:echo("Custom Component")
end
```

#### 2. Add to Main Initialization
```lua
function GUI.init()
    GUI.init_background()
    GUI.init_boxes()
    GUI.init_gauges()
    GUI.init_customComponent()  -- Add your component here
    -- ... other initialization
end
```

#### 3. Create Update Functions
```lua
function GUI.updateCustomComponent(data)
    if not GUI.customComponent then return end
    
    GUI.customComponent:echo(string.format("Data: %s", data))
end

-- Register for relevant events
registerAnonymousEventHandler("msdp.CUSTOM_DATA", "GUI.updateCustomComponent")
```

### Plugin Development

#### Plugin Template
```lua
-- CustomPlugin.lua
local CustomPlugin = {}

-- Plugin configuration
CustomPlugin.config = {
    enabled = true,
    updateInterval = 1000
}

-- Plugin initialization
function CustomPlugin.init()
    print("CustomPlugin initializing...")
    
    -- Create GUI elements
    CustomPlugin.createGUI()
    
    -- Register event handlers
    CustomPlugin.registerEvents()
    
    -- Start timers if needed
    CustomPlugin.startTimers()
end

-- Create plugin GUI
function CustomPlugin.createGUI()
    CustomPlugin.window = Geyser.UserWindow:new({
        name = "CustomPluginWindow",
        x = 100, y = 100,
        width = 300, height = 200
    })
    
    CustomPlugin.label = Geyser.Label:new({
        name = "CustomPluginLabel", 
        x = 0, y = 0,
        width = "100%", height = "100%"
    }, CustomPlugin.window)
end

-- Register event handlers
function CustomPlugin.registerEvents()
    registerAnonymousEventHandler("msdp.HEALTH", "CustomPlugin.onHealthChange")
end

-- Event handler example
function CustomPlugin.onHealthChange()
    if CustomPlugin.label then
        CustomPlugin.label:echo("Health: " .. msdp.HEALTH)
    end
end

-- Plugin cleanup
function CustomPlugin.cleanup()
    if CustomPlugin.window then
        CustomPlugin.window:hide()
    end
    killAnonymousEventHandler("CustomPlugin.onHealthChange")
end

-- Auto-initialize if LuminariGUI is loaded
if GUI and GUI.init then
    CustomPlugin.init()
else
    -- Wait for LuminariGUI to load
    registerAnonymousEventHandler("LuminariGUI.initialized", "CustomPlugin.init")
end

return CustomPlugin
```

### Integration with Existing Systems

#### YATCO Chat Integration
```lua
-- Add custom chat processing
function processCustomChat(line)
    -- Extract channel and message
    local channel, message = string.match(line, "^%[(%w+)%] (.+)$")
    
    if channel and demonnic.chat.config.channels[channel] then
        -- Route to existing channel
        demonnic.chat:echo(message, channel)
    else
        -- Create new channel if needed
        if channel then
            addCustomChannel(channel, {color = "white", timestamp = true})
            demonnic.chat:echo(message, channel)
        end
    end
end

-- Register trigger for custom chat format
customChatTrigger = tempTrigger("^%[%w+%] .+$", "processCustomChat")
```

## Code Examples

### Complete Custom Component Example

```lua
-- Weather Display Component
GUI.WeatherDisplay = {}

function GUI.WeatherDisplay.init()
    -- Create the weather display container
    GUI.weatherContainer = Geyser.Label:new({
        name = "weatherContainer",
        x = 10, y = 10, 
        width = 180, height = 60
    }, GUI.Right)
    
    GUI.weatherContainer:setStyleSheet([[
        background-color: rgba(0, 50, 100, 180);
        border: 2px solid #4A90E2;
        border-radius: 8px;
        color: white;
        font-family: Arial;
        font-size: 11pt;
        padding: 5px;
    ]])
    
    -- Initialize with default content
    GUI.WeatherDisplay.update("Unknown", "Clear")
    
    -- Register for weather updates (assuming custom MSDP variable)
    registerAnonymousEventHandler("msdp.WEATHER", "GUI.WeatherDisplay.onWeatherChange")
end

function GUI.WeatherDisplay.update(temperature, condition)
    if not GUI.weatherContainer then return end
    
    local html = string.format([[
        <div style="text-align: center;">
            <div style="font-size: 14pt; font-weight: bold;">%s</div>
            <div style="font-size: 10pt; color: #B0C4DE;">%s</div>
        </div>
    ]], temperature, condition)
    
    GUI.weatherContainer:echo(html)
end

function GUI.WeatherDisplay.onWeatherChange()
    if msdp.WEATHER then
        local temp = msdp.WEATHER.temperature or "Unknown"
        local condition = msdp.WEATHER.condition or "Clear"
        GUI.WeatherDisplay.update(temp, condition)
    end
end

-- Add to main GUI initialization
-- Add this line to GUI.init(): GUI.WeatherDisplay.init()
```

### Advanced MSDP Handler Example

```lua
-- Comprehensive combat tracker
GUI.CombatTracker = {}

function GUI.CombatTracker.init()
    GUI.CombatTracker.data = {
        inCombat = false,
        startTime = nil,
        damageDealt = 0,
        damageReceived = 0,
        lastHealth = nil
    }
    
    -- Register multiple MSDP events
    registerAnonymousEventHandler("msdp.HEALTH", "GUI.CombatTracker.onHealthChange")
    registerAnonymousEventHandler("msdp.OPPONENT_HEALTH", "GUI.CombatTracker.onOpponentChange")
    registerAnonymousEventHandler("msdp.OPPONENT_NAME", "GUI.CombatTracker.onOpponentChange")
end

function GUI.CombatTracker.onHealthChange()
    local currentHealth = tonumber(msdp.HEALTH)
    if not currentHealth then return end
    
    local data = GUI.CombatTracker.data
    
    if data.lastHealth and data.inCombat then
        local damage = data.lastHealth - currentHealth
        if damage > 0 then
            data.damageReceived = data.damageReceived + damage
            GUI.CombatTracker.updateDisplay()
        end
    end
    
    data.lastHealth = currentHealth
end

function GUI.CombatTracker.onOpponentChange()
    local data = GUI.CombatTracker.data
    
    if msdp.OPPONENT_NAME and msdp.OPPONENT_NAME ~= "" then
        -- Entering combat
        if not data.inCombat then
            data.inCombat = true
            data.startTime = getEpoch()
            data.damageDealt = 0
            data.damageReceived = 0
            print("Combat started with " .. msdp.OPPONENT_NAME)
        end
    else
        -- Leaving combat
        if data.inCombat then
            data.inCombat = false
            local duration = getEpoch() - data.startTime
            GUI.CombatTracker.displaySummary(duration)
        end
    end
    
    GUI.CombatTracker.updateDisplay()
end

function GUI.CombatTracker.updateDisplay()
    local data = GUI.CombatTracker.data
    
    if data.inCombat then
        local duration = getEpoch() - data.startTime
        local dps = data.damageDealt / math.max(duration, 1)
        
        local html = string.format([[
            Combat: %s<br/>
            Time: %ds<br/>
            Damage: %d (%.1f/s)<br/>
            Received: %d
        ]], msdp.OPPONENT_NAME or "Unknown", 
            duration, data.damageDealt, dps, data.damageReceived)
        
        -- Display in combat tracker component
        if GUI.combatTrackerLabel then
            GUI.combatTrackerLabel:echo(html)
        end
    end
end

function GUI.CombatTracker.displaySummary(duration)
    local data = GUI.CombatTracker.data
    local avgDPS = data.damageDealt / math.max(duration, 1)
    
    print(string.format("Combat Summary: %ds, %d damage dealt (%.1f DPS), %d received",
                       duration, data.damageDealt, avgDPS, data.damageReceived))
end
```

This API documentation provides comprehensive coverage of LuminariGUI's functionality for developers looking to understand, extend, or integrate with the system.