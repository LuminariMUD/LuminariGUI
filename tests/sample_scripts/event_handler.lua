-- Sample event handler for testing
local event_log = {}

function log_event(event_name, data)
    table.insert(event_log, {
        event = event_name,
        data = data,
        timestamp = os.time()
    })
end

function get_event_log()
    return event_log
end

function clear_event_log()
    event_log = {}
end

-- Mock event handlers
function on_room_change(event, room_data)
    log_event("room_change", room_data)
    print("Room changed to: " .. (room_data.NAME or "Unknown"))
end

function on_health_update(event, health, max_health)
    log_event("health_update", {health = health, max_health = max_health})
    local percent = math.floor((health / max_health) * 100)
    print("Health: " .. health .. "/" .. max_health .. " (" .. percent .. "%)")
end

function on_group_update(event, group_data)
    log_event("group_update", group_data)
    print("Group members: " .. #group_data)
    for i, member in ipairs(group_data) do
        print("  " .. member.NAME .. " (" .. member.LEVEL .. " " .. member.CLASS .. ")")
    end
end

-- Test event system
print("Testing event handlers...")

-- Test room change
on_room_change("msdp.ROOM", {
    VNUM = 3001,
    NAME = "Test Room",
    EXITS = {north = 3002}
})

-- Test health update
on_health_update("msdp.HEALTH", 85, 100)

-- Test group update
on_group_update("msdp.GROUP", {
    {NAME = "TestPlayer", LEVEL = 10, CLASS = "warrior"},
    {NAME = "Ally", LEVEL = 12, CLASS = "mage"}
})

print("Event log entries: " .. #get_event_log())
print("Event handler tests completed!")