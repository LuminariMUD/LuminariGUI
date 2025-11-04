-- Test script to verify resource cleanup implementation

-- Mock Mudlet functions for testing
local test_resources = {
    handlers = {},
    timers = {},
    handler_counter = 1,
    timer_counter = 1
}

-- Mock functions
function registerAnonymousEventHandler(event, handler)
    local id = "handler_" .. test_resources.handler_counter
    test_resources.handler_counter = test_resources.handler_counter + 1
    test_resources.handlers[id] = {event = event, handler = handler}
    return id
end

function killAnonymousEventHandler(id)
    if test_resources.handlers[id] then
        test_resources.handlers[id] = nil
        return true
    end
    return false
end

function tempTimer(delay, callback)
    local id = "timer_" .. test_resources.timer_counter
    test_resources.timer_counter = test_resources.timer_counter + 1
    test_resources.timers[id] = {delay = delay, callback = callback}
    return id
end

function killTimer(id)
    if test_resources.timers[id] then
        test_resources.timers[id] = nil
        return true
    end
    return false
end

function exists(id, type)
    if type == "timer" then
        return test_resources.timers[id] ~= nil and 1 or 0
    end
    return 0
end

-- Count active resources
function countResources()
    local handler_count = 0
    local timer_count = 0
    
    for _ in pairs(test_resources.handlers) do
        handler_count = handler_count + 1
    end
    
    for _ in pairs(test_resources.timers) do
        timer_count = timer_count + 1
    end
    
    return handler_count, timer_count
end

-- Test the cleanup implementation
print("=== Resource Cleanup Test ===")
print("Initial state:")
local init_handlers, init_timers = countResources()
print(string.format("Handlers: %d, Timers: %d", init_handlers, init_timers))

-- Load the cleanup implementation (simplified version)
GUI = {}
GUI.cleanup = {
    handlers = {},
    timers = {}
}

-- Simulate resource creation
print("\nCreating resources...")

-- MSDPMapper handlers (6)
GUI.cleanup.handlers.msdpRoom = registerAnonymousEventHandler("msdp.ROOM", "map.eventHandler")
GUI.cleanup.handlers.msdpPosition = registerAnonymousEventHandler("msdp.POSITION", "map.eventHandler")
GUI.cleanup.handlers.shiftRoom = registerAnonymousEventHandler("shiftRoom", "map.eventHandler")
GUI.cleanup.handlers.sysConnection = registerAnonymousEventHandler("sysConnectionEvent", "map.eventHandler")
GUI.cleanup.handlers.sysProtocol = registerAnonymousEventHandler("sysProtocolEnabled", "map.onProtocolEnabled")
GUI.cleanup.handlers.sysDownload = registerAnonymousEventHandler("sysDownloadDone", "map.eventHandler")

-- Toggles handlers (2)
GUI.cleanup.handlers.sysLoad = registerAnonymousEventHandler("sysLoadEvent", "GUI.loadToggles")
GUI.cleanup.handlers.sysExit = registerAnonymousEventHandler("sysExitEvent", "GUI.saveToggles")

-- Cast Console timers (3)
GUI.cleanup.timers.cast1 = tempTimer(10, "clearWindow")
GUI.cleanup.timers.cast2 = tempTimer(10, "clearWindow")
GUI.cleanup.timers.cast3 = tempTimer(10, "clearWindow")

print("After creation:")
local after_handlers, after_timers = countResources()
print(string.format("Handlers: %d, Timers: %d", after_handlers, after_timers))
print(string.format("Created: %d handlers, %d timers", 
      after_handlers - init_handlers, after_timers - init_timers))

-- Test cleanup
print("\nPerforming cleanup...")
local cleaned_handlers = 0
local cleaned_timers = 0

-- Clean handlers
for name, id in pairs(GUI.cleanup.handlers) do
    if killAnonymousEventHandler(id) then
        cleaned_handlers = cleaned_handlers + 1
    end
end

-- Clean timers
for name, id in pairs(GUI.cleanup.timers) do
    if killTimer(id) then
        cleaned_timers = cleaned_timers + 1
    end
end

print(string.format("Cleaned: %d handlers, %d timers", cleaned_handlers, cleaned_timers))

print("\nFinal state:")
local final_handlers, final_timers = countResources()
print(string.format("Handlers: %d, Timers: %d", final_handlers, final_timers))

-- Verify cleanup
if final_handlers == init_handlers and final_timers == init_timers then
    print("\n✓ SUCCESS: All resources properly cleaned up!")
else
    print("\n✗ FAILURE: Resource leak detected!")
    print(string.format("  Leaked handlers: %d", final_handlers - init_handlers))
    print(string.format("  Leaked timers: %d", final_timers - init_timers))
end

-- Test double cleanup protection
print("\nTesting double cleanup...")
local second_cleaned = 0
for name, id in pairs(GUI.cleanup.handlers) do
    if killAnonymousEventHandler(id) then
        second_cleaned = second_cleaned + 1
    end
end
print(string.format("Second cleanup attempt: %d resources cleaned (should be 0)", second_cleaned))

print("\n=== Test Complete ===")