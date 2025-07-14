-- Performance test script
local performance = {}

function performance.time_function(func, iterations)
    local start_time = os.clock()
    
    for i = 1, iterations do
        func()
    end
    
    local end_time = os.clock()
    return (end_time - start_time) * 1000 -- Convert to milliseconds
end

-- Test functions
function string_operations()
    local str = "The quick brown fox jumps over the lazy dog"
    local result = str:upper():gsub(" ", "_"):sub(1, 20)
    return result
end

function table_operations()
    local tbl = {}
    for i = 1, 100 do
        tbl[i] = math.random(1, 1000)
    end
    table.sort(tbl)
    return #tbl
end

function math_operations()
    local result = 0
    for i = 1, 100 do
        result = result + math.sin(i) * math.cos(i)
    end
    return result
end

function room_simulation()
    local room = {
        vnum = 1001,
        name = "Test Room",
        exits = {},
        coords = {x = 0, y = 0, z = 0}
    }
    
    -- Simulate room processing
    for dir, target in pairs({n = 1002, s = 1000, e = 1003, w = 999}) do
        room.exits[dir] = target
    end
    
    return room
end

-- Run performance tests
print("Running performance tests...")

local tests = {
    {name = "String Operations", func = string_operations, iterations = 1000},
    {name = "Table Operations", func = table_operations, iterations = 100},
    {name = "Math Operations", func = math_operations, iterations = 100},
    {name = "Room Simulation", func = room_simulation, iterations = 1000}
}

for _, test in ipairs(tests) do
    local elapsed = performance.time_function(test.func, test.iterations)
    local per_op = elapsed / test.iterations
    print(string.format("%s: %.2fms total, %.4fms per operation", 
          test.name, elapsed, per_op))
end

print("Performance tests completed!")