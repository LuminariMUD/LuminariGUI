-- Resource Cleanup Implementation for LuminariGUI
-- This script shows how to implement proper resource cleanup

-- Initialize cleanup storage at package level
GUI = GUI or {}
GUI.cleanup = GUI.cleanup or {
    handlers = {},
    timers = {},
    aliases = {}
}

-- Helper function to safely store handler IDs
function GUI.registerHandler(event, handler, name)
    local id = registerAnonymousEventHandler(event, handler)
    if name then
        GUI.cleanup.handlers[name] = id
    else
        table.insert(GUI.cleanup.handlers, id)
    end
    return id
end

-- Helper function to safely create timers
function GUI.createTimer(delay, callback, name)
    local id = tempTimer(delay, callback)
    if name then
        GUI.cleanup.timers[name] = id
    else
        table.insert(GUI.cleanup.timers, id)
    end
    return id
end

-- Main cleanup function
function GUI.performCleanup()
    local cleaned = {handlers = 0, timers = 0}
    
    -- Clean up handlers
    for key, id in pairs(GUI.cleanup.handlers) do
        if id then
            local success = pcall(killAnonymousEventHandler, id)
            if success then
                cleaned.handlers = cleaned.handlers + 1
            end
        end
    end
    
    -- Clean up timers
    for key, id in pairs(GUI.cleanup.timers) do
        if id and exists(id, "timer") then
            killTimer(id)
            cleaned.timers = cleaned.timers + 1
        end
    end
    
    -- Clean up aliases (from map system)
    if map and map.aliases then
        for key, id in pairs(map.aliases) do
            if id and exists(id, "alias") then
                killAlias(id)
            end
        end
    end
    
    -- Reset storage
    GUI.cleanup.handlers = {}
    GUI.cleanup.timers = {}
    
    return cleaned
end

-- Updated registration examples for each component:

-- 1. MSDPMapper handlers (replace lines 1415-1420)
GUI.cleanup.handlers.msdpRoom = registerAnonymousEventHandler("msdp.ROOM", "map.eventHandler")
GUI.cleanup.handlers.msdpPosition = registerAnonymousEventHandler("msdp.POSITION", "map.eventHandler")
GUI.cleanup.handlers.shiftRoom = registerAnonymousEventHandler("shiftRoom", "map.eventHandler")
GUI.cleanup.handlers.sysConnection = registerAnonymousEventHandler("sysConnectionEvent", "map.eventHandler")
GUI.cleanup.handlers.sysProtocol = registerAnonymousEventHandler("sysProtocolEnabled", "map.onProtocolEnabled")
GUI.cleanup.handlers.sysDownload = registerAnonymousEventHandler("sysDownloadDone", "map.eventHandler")

-- 2. Toggles handlers (replace lines 1536-1537)
GUI.cleanup.handlers.sysLoad = registerAnonymousEventHandler("sysLoadEvent", "GUI.loadToggles")
GUI.cleanup.handlers.sysExit = registerAnonymousEventHandler("sysExitEvent", "GUI.saveToggles")

-- 3. Cast Console timer fix (update the timer creation functions)
function GUI.castConsole_completeCast()
    GUI.castConsole:cecho("\n<white>Spell: <yellow>"..GUI.currentlyCasting:title().." <white>- <green>Cast")
    -- Kill any existing timer before creating new one
    if GUI.castConsoleTimer then
        killTimer(GUI.castConsoleTimer)
    end
    GUI.castConsoleTimer = GUI.createTimer(10, [[clearUserWindow("GUI.castConsole")]], "castConsoleTimer")
end

-- 4. Config script handlers (example for a few - lines 3385+)
GUI.cleanup.handlers.msdpGroup = registerAnonymousEventHandler("msdp.GROUP", "GUI.updateGroup")
GUI.cleanup.handlers.msdpAffects = registerAnonymousEventHandler("msdp.AFFECTS", "GUI.updateAffectIcons")
-- ... continue for all 33 handlers ...

-- 5. Register cleanup on package events
GUI.cleanup.handlers.uninstall = registerAnonymousEventHandler("sysUninstallPackage", function(_, package)
    if package == "LuminariGUI" then
        local result = GUI.performCleanup()
        print(string.format("LuminariGUI cleanup complete: %d handlers, %d timers removed", 
              result.handlers, result.timers))
    end
end)

-- Also clean up on exit
GUI.cleanup.handlers.exitCleanup = registerAnonymousEventHandler("sysExitEvent", function()
    GUI.performCleanup()
end)

-- Manual cleanup command for testing
function cleanupLuminariGUI()
    local result = GUI.performCleanup()
    cecho(string.format("\n<green>LuminariGUI cleanup complete: <yellow>%d<green> handlers, <yellow>%d<green> timers removed\n", 
          result.handlers, result.timers))
end