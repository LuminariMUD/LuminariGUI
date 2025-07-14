-- Simple function for unit testing
function add_numbers(a, b)
    return a + b
end

function multiply_numbers(a, b)
    return a * b
end

function string_length(str)
    return string.len(str)
end

function table_contains(tbl, value)
    for _, v in ipairs(tbl) do
        if v == value then
            return true
        end
    end
    return false
end

function clamp_value(value, min_val, max_val)
    return math.max(min_val, math.min(max_val, value))
end

-- Test the functions
assert(add_numbers(2, 3) == 5, "Addition test failed")
assert(multiply_numbers(4, 5) == 20, "Multiplication test failed")
assert(string_length("hello") == 5, "String length test failed")
assert(table_contains({1, 2, 3}, 2) == true, "Table contains test failed")
assert(clamp_value(15, 1, 10) == 10, "Clamp test failed")

print("All simple function tests passed!")