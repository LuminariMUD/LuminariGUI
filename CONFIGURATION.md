# LuminariGUI Configuration Guide

This document provides comprehensive configuration options for LuminariGUI, including default settings, customization examples, and advanced configuration scenarios.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [GUI Layout Configuration](#gui-layout-configuration)
- [Chat System Configuration](#chat-system-configuration)
- [Display Settings](#display-settings)
- [MSDP Configuration](#msdp-configuration)
- [Performance Settings](#performance-settings)
- [Advanced Customization](#advanced-customization)
- [Troubleshooting](#troubleshooting)

## Configuration Overview

LuminariGUI uses multiple configuration systems:

1. **Core GUI Configuration** - Layout, styling, and component settings
2. **YATCO Chat Configuration** - Channel settings, display options, and chat behavior
3. **MSDP Configuration** - Protocol settings and variable requests
4. **User Preferences** - Personal customizations and toggles

### Configuration File Locations

```lua
-- Core configuration stored in GUI namespace
GUI.config = {...}

-- YATCO configuration in demonnic namespace  
demonnic.chat.config = {...}

-- Package configuration
config.lua  -- Package metadata
```

### Default Configuration Structure

```lua
GUI.config = {
    layout = {
        leftPanelWidth = 300,
        rightPanelWidth = 250, 
        bottomPanelHeight = 200,
        gaugePanelHeight = 40
    },
    display = {
        showMap = true,
        showChat = true,
        showStatusGauges = true,
        showControlButtons = true,
        showTabbedInfo = true
    },
    gauges = {
        showPercentages = true,
        animateChanges = true,
        updateFrequency = 100,
        colorThresholds = {
            health = {low = 25, medium = 50},
            movement = {low = 20, medium = 40}
        }
    },
    styling = {
        theme = "default",
        transparency = 180,
        fontSize = 12,
        fontFamily = "Arial"
    }
}
```

## GUI Layout Configuration

### Panel Dimensions

Configure the main layout panels:

```lua
-- Adjust left panel width (character info area)
GUI.config.layout.leftPanelWidth = 350  -- Default: 300

-- Adjust right panel width (map/controls area) 
GUI.config.layout.rightPanelWidth = 280  -- Default: 250

-- Adjust bottom panel height (chat/status area)
GUI.config.layout.bottomPanelHeight = 250  -- Default: 200

-- Adjust status gauge panel height
GUI.config.layout.gaugePanelHeight = 50  -- Default: 40
```

### Component Positioning

Fine-tune individual component positions:

```lua
-- Custom component positioning
GUI.config.positions = {
    healthGauge = {x = 5, y = 5, width = 120, height = 25},
    movesGauge = {x = 130, y = 5, width = 120, height = 25},
    experienceGauge = {x = 255, y = 5, width = 150, height = 25},
    enemyGauge = {x = 410, y = 5, width = 100, height = 25},
    
    controlButtons = {
        map = {x = 5, y = 5, width = 60, height = 25},
        chat = {x = 70, y = 5, width = 60, height = 25},
        help = {x = 135, y = 5, width = 60, height = 25}
    }
}
```

### Visibility Toggles

Control which components are visible by default:

```lua
-- Component visibility settings
GUI.config.display = {
    showMap = true,           -- Show/hide map panel
    showChat = true,          -- Show/hide chat panel
    showStatusGauges = true,  -- Show/hide status gauges
    showControlButtons = true, -- Show/hide control buttons
    showTabbedInfo = true,    -- Show/hide tabbed info window
    showActionIcons = true,   -- Show/hide action icons
    showAffectIcons = true,   -- Show/hide spell affect icons
    showGroupInfo = true      -- Show/hide group information
}
```

## Chat System Configuration

### YATCO Channel Settings

Configure chat channels and their behavior:

```lua
demonnic.chat.config = {
    -- Channel definitions
    channels = {
        all = {
            color = "white",
            timestamp = true,
            timestampFormat = "[HH:mm:ss] ",
            blink = false,
            preserveBackground = false
        },
        chat = {
            color = "white",
            timestamp = true,
            timestampFormat = "[HH:mm:ss] ",
            blink = true,
            preserveBackground = false
        },
        tell = {
            color = "cyan",
            timestamp = true,
            timestampFormat = "[HH:mm:ss] ",
            blink = true,
            preserveBackground = true
        },
        group = {
            color = "yellow",
            timestamp = true,
            timestampFormat = "[HH:mm:ss] ",
            blink = false,
            preserveBackground = false
        },
        ooc = {
            color = "magenta",
            timestamp = true,
            timestampFormat = "[HH:mm:ss] ",
            blink = false,
            preserveBackground = false
        }
    },
    
    -- Tab display settings
    tabFont = "Arial",
    tabFontSize = 10,
    activeTabColor = "#4A90E2",
    inactiveTabColor = "#2C2C2C",
    blinkingTabColor = "#FF6B6B",
    
    -- Chat window settings
    chatHeight = 150,
    maxScrollback = 1000,
    wordWrap = true,
    showTimestamps = true
}
```

### Custom Channel Creation

Add new chat channels:

```lua
-- Add a guild channel
demonnic.chat.config.channels.guild = {
    color = "green",
    timestamp = true,
    timestampFormat = "[HH:mm:ss] ",
    blink = true,
    preserveBackground = false
}

-- Add a newbie channel  
demonnic.chat.config.channels.newbie = {
    color = "lightblue",
    timestamp = true,
    timestampFormat = "[HH:mm:ss] ",
    blink = false,
    preserveBackground = false
}

-- Function to add channels dynamically
function addChatChannel(name, config)
    demonnic.chat.config.channels[name] = config
    if demonnic.chat then
        demonnic.chat:addTab(name)
    end
end
```

### Chat Triggers Configuration

Configure chat message routing:

```lua
-- Chat trigger patterns
GUI.chatTriggers = {
    {
        pattern = "^(.+) chats '(.+)'$",
        channel = "chat",
        format = function(matches)
            return string.format("%s chats '%s'", matches[2], matches[3])
        end
    },
    {
        pattern = "^(.+) tells you '(.+)'$", 
        channel = "tell",
        format = function(matches)
            return string.format("%s tells you '%s'", matches[2], matches[3])
        end
    },
    {
        pattern = "^(.+) group-says '(.+)'$",
        channel = "group", 
        format = function(matches)
            return string.format("%s group-says '%s'", matches[2], matches[3])
        end
    }
}
```

## Display Settings

### Color Themes

Configure visual themes and colors:

```lua
-- Default color theme
GUI.themes.default = {
    background = "rgba(0, 0, 0, 180)",
    border = "#666666",
    text = "#FFFFFF",
    accent = "#4A90E2",
    
    gauges = {
        health = {
            high = "#00FF00",    -- Green for high health
            medium = "#FFFF00",  -- Yellow for medium health
            low = "#FF0000"      -- Red for low health
        },
        movement = {
            high = "#00FFFF",    -- Cyan for high movement
            medium = "#FFFF00",  -- Yellow for medium movement 
            low = "#FF6600"      -- Orange for low movement
        },
        experience = {
            bar = "#9966FF",     -- Purple for experience
            text = "#FFFFFF"
        },
        enemy = {
            bar = "#FF4444",     -- Red for enemy health
            text = "#FFFFFF"
        }
    }
}

-- Dark theme variant
GUI.themes.dark = {
    background = "rgba(20, 20, 20, 200)",
    border = "#444444",
    text = "#CCCCCC", 
    accent = "#6A9BD2",
    
    gauges = {
        health = {high = "#22AA22", medium = "#CCCC22", low = "#CC2222"},
        movement = {high = "#22AAAA", medium = "#CCCC22", low = "#CC6622"},
        experience = {bar = "#8855CC", text = "#CCCCCC"},
        enemy = {bar = "#CC3333", text = "#CCCCCC"}
    }
}
```

### Font Configuration

Configure fonts and text display:

```lua
GUI.config.fonts = {
    default = {
        family = "Arial",
        size = 12,
        weight = "normal"
    },
    gauges = {
        family = "Arial",
        size = 11, 
        weight = "bold"
    },
    buttons = {
        family = "Arial",
        size = 10,
        weight = "normal"
    },
    chat = {
        family = "Consolas", -- Monospace for chat
        size = 11,
        weight = "normal"
    }
}
```

### Transparency Settings

Configure component transparency:

```lua
GUI.config.transparency = {
    background = 180,      -- Main background (0-255)
    panels = 150,          -- Panel backgrounds
    gauges = 200,          -- Status gauges
    buttons = 180,         -- Control buttons
    chat = 160            -- Chat windows
}
```

## MSDP Configuration

### Variable Requests

Configure which MSDP variables to request:

```lua
GUI.msdpConfig = {
    -- Core character variables
    character = {
        "HEALTH", "MAX_HEALTH",
        "MOVEMENT", "MAX_MOVEMENT", 
        "EXPERIENCE", "EXPERIENCE_TNL",
        "LEVEL", "CLASS", "RACE"
    },
    
    -- Combat variables
    combat = {
        "OPPONENT_HEALTH", "OPPONENT_NAME",
        "ACTIONS", "COMBAT_STATE"
    },
    
    -- Environment variables
    environment = {
        "ROOM", "ROOM_NAME", "ROOM_EXITS",
        "AREA_NAME", "WORLD_TIME"
    },
    
    -- Social variables
    social = {
        "GROUP", "AFFECTS", "PARTY"
    },
    
    -- Custom variables (server-specific)
    custom = {
        "WEATHER", "REPUTATION", "GUILD_RANK"
    }
}

-- Function to request all configured variables
function GUI.requestMSDPVariables()
    for category, variables in pairs(GUI.msdpConfig) do
        for _, variable in ipairs(variables) do
            sendMSDP("REQUEST", variable)
        end
    end
end
```

### MSDP Update Frequencies

Control how often MSDP variables are updated:

```lua
GUI.msdpFrequencies = {
    -- High frequency updates (every 100ms)
    fast = {
        variables = {"HEALTH", "MOVEMENT", "OPPONENT_HEALTH"},
        interval = 100
    },
    
    -- Medium frequency updates (every 500ms)
    medium = {
        variables = {"EXPERIENCE", "ACTIONS", "AFFECTS"},
        interval = 500  
    },
    
    -- Low frequency updates (every 2000ms)
    slow = {
        variables = {"ROOM", "GROUP", "AREA_NAME"},
        interval = 2000
    }
}
```

## Performance Settings

### Update Optimization

Configure update frequencies and performance settings:

```lua
GUI.config.performance = {
    -- GUI update frequencies (milliseconds)
    gaugeUpdateFreq = 100,     -- Status gauge updates
    mapUpdateFreq = 500,       -- Map display updates 
    chatUpdateFreq = 50,       -- Chat message processing
    iconUpdateFreq = 1000,     -- Action/affect icon updates
    
    -- Memory management
    maxChatHistory = 1000,     -- Maximum chat lines to keep
    maxMapNodes = 5000,        -- Maximum map nodes in memory
    garbageCollectFreq = 30000, -- Lua garbage collection frequency
    
    -- Visual performance
    animateGauges = true,      -- Enable gauge animations
    animationSpeed = 200,      -- Animation duration (ms)
    reduceTransparency = false, -- Reduce transparency for performance
    limitFPS = false           -- Limit GUI updates to reduce CPU usage
}
```

### Memory Management

Configure memory usage and cleanup:

```lua
GUI.config.memory = {
    -- Automatic cleanup settings
    autoCleanup = true,
    cleanupInterval = 60000,   -- 1 minute
    
    -- Component cleanup thresholds
    maxEventHandlers = 100,
    maxTimers = 50,
    maxTriggers = 200,
    
    -- Data retention limits
    maxHistoryEntries = 500,
    maxLogEntries = 1000,
    maxCacheSize = 5000       -- Maximum cached objects
}
```

## Advanced Customization

### Custom Component Layouts

Create custom layouts for different screen sizes:

```lua
-- Layout profiles for different screen resolutions
GUI.layoutProfiles = {
    small = {  -- For smaller screens (1024x768)
        leftPanelWidth = 250,
        rightPanelWidth = 200,
        bottomPanelHeight = 150,
        fontSize = 10,
        compactMode = true
    },
    
    medium = { -- For medium screens (1280x1024) 
        leftPanelWidth = 300,
        rightPanelWidth = 250,
        bottomPanelHeight = 200,
        fontSize = 12,
        compactMode = false
    },
    
    large = {  -- For large screens (1920x1080+)
        leftPanelWidth = 400,
        rightPanelWidth = 300,
        bottomPanelHeight = 250,
        fontSize = 14,
        compactMode = false
    }
}

-- Function to apply layout profile
function GUI.applyLayoutProfile(profileName)
    local profile = GUI.layoutProfiles[profileName]
    if not profile then return end
    
    for key, value in pairs(profile) do
        GUI.config.layout[key] = value
    end
    
    -- Refresh GUI with new layout
    GUI.refresh()
end
```

### Custom Styling

Advanced CSS styling for components:

```lua
GUI.customStyles = {
    modernGauges = [[
        QProgressBar {
            border: 2px solid #4A90E2;
            border-radius: 8px;
            background-color: rgba(30, 30, 30, 200);
            text-align: center;
            font-weight: bold;
            color: white;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4A90E2, stop:1 #2171B5);
            border-radius: 6px;
        }
    ]],
    
    glassButtons = [[
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,50), stop:1 rgba(255,255,255,20));
            border: 1px solid rgba(255,255,255,80);
            border-radius: 6px;
            color: white;
            font-weight: bold;
            padding: 4px 8px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,80), stop:1 rgba(255,255,255,40));
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,20), stop:1 rgba(255,255,255,50));
        }
    ]]
}
```

### Event-Based Customization

Advanced event handling and customization:

```lua
-- Custom event handlers for advanced features
GUI.customEvents = {
    onHealthCritical = function(health, maxHealth)
        local percentage = (health / maxHealth) * 100
        if percentage <= 10 then
            -- Flash screen red
            GUI.flashWarning("CRITICAL HEALTH!", "red")
            
            -- Play sound (if available)
            if playSound then
                playSound("critical_health.wav")
            end
            
            -- Send emergency commands
            send("wimpy 90")
            send("flee")
        end
    end,
    
    onLevelUp = function(newLevel)
        GUI.showCelebration("LEVEL UP!", string.format("Welcome to level %d!", newLevel))
        
        -- Log achievement
        GUI.logAchievement("level", newLevel, getEpoch())
        
        -- Request updated stats
        sendMSDP("REQUEST", "HEALTH")
        sendMSDP("REQUEST", "MAX_HEALTH")
    end,
    
    onCombatStart = function(opponent)
        -- Start combat timer
        GUI.combatStartTime = getEpoch()
        
        -- Enable combat-specific UI elements
        GUI.showCombatMode(true)
        
        -- Log combat start
        GUI.logCombat("start", opponent, getEpoch())
    end
}

-- Register custom events
registerAnonymousEventHandler("msdp.HEALTH", function()
    if msdp.HEALTH and msdp.MAX_HEALTH then
        GUI.customEvents.onHealthCritical(tonumber(msdp.HEALTH), tonumber(msdp.MAX_HEALTH))
    end
end)
```

### Plugin Configuration

Configuration for plugin development:

```lua
GUI.pluginConfig = {
    -- Plugin directories
    pluginPath = getMudletHomeDir() .. "/LuminariGUI_Plugins/",
    
    -- Plugin loading settings
    autoLoadPlugins = true,
    loadOrder = {"core", "ui", "data", "optional"},
    
    -- Plugin API settings
    allowFileAccess = false,    -- Restrict file system access
    allowNetworkAccess = false, -- Restrict network access
    sandboxMode = true,         -- Run plugins in sandbox
    
    -- Plugin data sharing
    sharedData = {
        allowRead = true,
        allowWrite = false,
        dataPath = getMudletHomeDir() .. "/LuminariGUI_Data/"
    }
}
```

## Troubleshooting

### Common Configuration Issues

#### Layout Problems

```lua
-- Reset layout to defaults
function GUI.resetLayout()
    GUI.config.layout = {
        leftPanelWidth = 300,
        rightPanelWidth = 250,
        bottomPanelHeight = 200,
        gaugePanelHeight = 40
    }
    GUI.refresh()
    print("Layout reset to defaults")
end

-- Validate layout values
function GUI.validateLayout()
    local layout = GUI.config.layout
    local issues = {}
    
    if layout.leftPanelWidth < 200 or layout.leftPanelWidth > 500 then
        table.insert(issues, "leftPanelWidth should be between 200-500")
    end
    
    if layout.rightPanelWidth < 200 or layout.rightPanelWidth > 400 then
        table.insert(issues, "rightPanelWidth should be between 200-400")
    end
    
    if #issues > 0 then
        print("Layout validation issues:")
        for _, issue in ipairs(issues) do
            print("  - " .. issue)
        end
        return false
    end
    
    return true
end
```

#### MSDP Connection Issues

```lua
-- Diagnose MSDP problems
function GUI.diagnoseMSDP()
    print("MSDP Diagnosis:")
    print("Protocol enabled:", msdp and "Yes" or "No")
    
    if msdp then
        print("Available variables:")
        for var, value in pairs(msdp) do
            print(string.format("  %s = %s", var, tostring(value)))
        end
    else
        print("MSDP not available. Check server settings.")
        print("Try: MSDP ON")
    end
end

-- Reset MSDP configuration
function GUI.resetMSDP()
    print("Resetting MSDP configuration...")
    
    -- Clear existing handlers
    for _, variable in ipairs({"HEALTH", "MOVEMENT", "EXPERIENCE", "ROOM", "GROUP"}) do
        local eventName = "msdp." .. variable
        if eventHandlers and eventHandlers[eventName] then
            killAnonymousEventHandler(eventName)
        end
    end
    
    -- Re-register handlers
    GUI.registerMSDPHandlers()
    
    -- Request variables again
    GUI.requestMSDPVariables()
    
    print("MSDP reset complete")
end
```

#### Chat System Issues

```lua
-- Fix chat display problems
function GUI.fixChatDisplay()
    print("Fixing chat display...")
    
    -- Reset YATCO configuration
    if demonnic and demonnic.chat then
        demonnic.chat:clear()
        
        -- Recreate tabs
        for channel, config in pairs(demonnic.chat.config.channels) do
            demonnic.chat:addTab(channel)
        end
        
        print("Chat tabs recreated")
    else
        print("YATCO not available. Check installation.")
    end
end

-- Clear chat history
function GUI.clearChatHistory()
    if demonnic and demonnic.chat then
        for channel, _ in pairs(demonnic.chat.config.channels) do
            demonnic.chat:clear(channel)
        end
        print("Chat history cleared")
    end
end
```

### Performance Troubleshooting

```lua
-- Performance monitoring
function GUI.checkPerformance()
    print("Performance Check:")
    
    -- Memory usage
    local memBefore = collectgarbage("count")
    collectgarbage()
    local memAfter = collectgarbage("count")
    
    print(string.format("Memory usage: %.2f KB (freed %.2f KB)", 
                       memAfter, memBefore - memAfter))
    
    -- Timer count
    local timerCount = 0
    if timers then
        for _ in pairs(timers) do
            timerCount = timerCount + 1
        end
    end
    print("Active timers:", timerCount)
    
    -- Event handler count  
    local handlerCount = 0
    if eventHandlers then
        for _ in pairs(eventHandlers) do
            handlerCount = handlerCount + 1
        end
    end
    print("Event handlers:", handlerCount)
    
    -- Recommendations
    if timerCount > 20 then
        print("WARNING: High timer count may affect performance")
    end
    
    if handlerCount > 50 then
        print("WARNING: High event handler count may affect performance")
    end
end

-- Clean up resources
function GUI.cleanup()
    print("Cleaning up LuminariGUI resources...")
    
    -- Kill timers
    if GUI.timers then
        for _, timerID in pairs(GUI.timers) do
            killTimer(timerID)
        end
        GUI.timers = {}
    end
    
    -- Remove event handlers
    if GUI.eventHandlers then
        for _, handlerID in pairs(GUI.eventHandlers) do
            killAnonymousEventHandler(handlerID)
        end
        GUI.eventHandlers = {}
    end
    
    -- Force garbage collection
    collectgarbage()
    
    print("Cleanup complete")
end
```

### Configuration Validation

```lua
-- Validate entire configuration
function GUI.validateConfig()
    local valid = true
    local issues = {}
    
    -- Check layout configuration
    if not GUI.validateLayout() then
        valid = false
        table.insert(issues, "Layout configuration invalid")
    end
    
    -- Check chat configuration
    if not demonnic or not demonnic.chat then
        valid = false
        table.insert(issues, "Chat system not available")
    end
    
    -- Check MSDP configuration
    if not msdp then
        valid = false
        table.insert(issues, "MSDP not available")
    end
    
    -- Report results
    if valid then
        print("Configuration validation passed")
    else
        print("Configuration validation failed:")
        for _, issue in ipairs(issues) do
            print("  - " .. issue)
        end
    end
    
    return valid
end
```

This configuration guide provides comprehensive control over all aspects of LuminariGUI's behavior and appearance, enabling users to customize the system to their specific needs and preferences.