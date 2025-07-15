#!/usr/bin/env python3

"""
State Validation Testing
========================
Tests for the new state validation system to ensure shared state corruption
is properly handled and prevented.
"""

import subprocess
import tempfile
import os
import sys

def create_test_lua_script():
    """Create a Lua script to test state validation functions"""
    return '''
-- Test State Validation Functions
local tests_passed = 0
local tests_failed = 0

function test_msdp_validation()
    -- Test 1: Valid MSDP data
    msdp = {
        HEALTH = 100,
        HEALTH_MAX = 150,
        MOVEMENT = 200,
        CHARACTER_NAME = "TestPlayer",
        ROOM = {
            VNUM = 1001,
            NAME = "Test Room",
            EXITS = {north = 1002, south = 1000}
        },
        AFFECTS = {
            AFFECTED_BY = {
                {NAME = "Hasted"},
                {NAME = "Protected"}
            }
        },
        GROUP = {
            {NAME = "Player1", HEALTH = 100, IS_LEADER = true},
            {NAME = "Player2", HEALTH = 80, IS_LEADER = false}
        }
    }
    
    -- Test basic MSDP validation
    assert(GUI.getMSDPHealth() == 100, "Health validation failed")
    assert(GUI.getMSDPMaxHealth() == 150, "Max health validation failed")
    assert(GUI.getMSDPMovement() == 200, "Movement validation failed")
    assert(GUI.getMSDPCharacterName() == "TestPlayer", "Character name validation failed")
    
    local room = GUI.getMSDPRoom()
    assert(room.VNUM == 1001, "Room VNUM validation failed")
    assert(room.NAME == "Test Room", "Room name validation failed")
    
    local affects = GUI.getMSDPAffects()
    assert(#affects.AFFECTED_BY == 2, "Affects validation failed")
    assert(affects.AFFECTED_BY[1].NAME == "Hasted", "First affect validation failed")
    
    local group = GUI.getMSDPGroup()
    assert(#group == 2, "Group validation failed")
    assert(group[1].NAME == "Player1", "Group member validation failed")
    
    print("✓ MSDP validation tests passed")
    tests_passed = tests_passed + 1
    
    -- Test 2: Invalid/missing MSDP data
    msdp = nil
    
    assert(GUI.getMSDPHealth() == 0, "Nil MSDP health default failed")
    assert(GUI.getMSDPCharacterName() == "Unknown", "Nil MSDP character name default failed")
    
    local room_nil = GUI.getMSDPRoom()
    assert(type(room_nil) == "table", "Nil MSDP room should return empty table")
    
    print("✓ MSDP nil handling tests passed")
    tests_passed = tests_passed + 1
    
    -- Test 3: Corrupted MSDP data
    msdp = {
        HEALTH = "not_a_number",
        ROOM = "not_a_table",
        AFFECTS = {AFFECTED_BY = "not_an_array"}
    }
    
    assert(GUI.getMSDPHealth() == 0, "Invalid MSDP health should return default")
    
    local room_corrupt = GUI.getMSDPRoom()
    assert(type(room_corrupt) == "table", "Corrupted MSDP room should return empty table")
    
    print("✓ MSDP corruption handling tests passed")
    tests_passed = tests_passed + 1
end

function test_toggle_validation()
    -- Test 1: Normal toggle operation
    GUI.toggles = {gagChat = true, includeInGroup = false}
    
    assert(GUI.getToggle("gagChat", false) == true, "Toggle read failed")
    assert(GUI.getToggle("includeInGroup", true) == false, "Toggle read failed")
    
    GUI.setToggle("gagChat", false)
    assert(GUI.getToggle("gagChat", true) == false, "Toggle write failed")
    
    print("✓ Toggle validation tests passed")
    tests_passed = tests_passed + 1
    
    -- Test 2: Corrupted toggles table
    GUI.toggles = nil
    
    local default_value = GUI.getToggle("gagChat", true)
    assert(default_value == true, "Corrupted toggles should return default")
    assert(type(GUI.toggles) == "table", "Corrupted toggles should be recovered")
    
    GUI.toggles = "not_a_table"
    local default_value2 = GUI.getToggle("includeInGroup", false)
    -- The function reinitializes with defaults, so includeInGroup becomes true
    assert(default_value2 == true, "String toggles should be reinitialized with defaults")
    assert(type(GUI.toggles) == "table", "Corrupted toggles should be recovered to table")
    
    print("✓ Toggle corruption handling tests passed")
    tests_passed = tests_passed + 1
end

function test_room_info_validation()
    -- Test 1: Valid room info
    map = {
        room_info = {
            VNUM = 1001,
            ENVIRONMENT = "Room",
            TERRAIN = "Inside",
            EXITS = {north = 1002}
        }
    }
    
    assert(GUI.validateRoomInfo("VNUM", nil) == 1001, "Room VNUM validation failed")
    assert(GUI.validateRoomInfo("ENVIRONMENT", "Unknown") == "Room", "Room environment validation failed")
    
    print("✓ Room info validation tests passed")
    tests_passed = tests_passed + 1
    
    -- Test 2: Missing room info
    map = nil
    
    assert(GUI.validateRoomInfo("VNUM", 999) == 999, "Missing map should return default")
    
    map = {room_info = nil}
    assert(GUI.validateRoomInfo("ENVIRONMENT", "Default") == "Default", "Missing room_info should return default")
    
    print("✓ Room info missing handling tests passed")
    tests_passed = tests_passed + 1
end

function test_state_recovery()
    -- Test state recovery functionality
    GUI.toggles = nil
    map = nil
    
    GUI.recoverCorruptedState()
    
    assert(type(GUI.toggles) == "table", "State recovery should restore toggles")
    assert(type(map) == "table", "State recovery should restore map")
    assert(type(map.room_info) == "table", "State recovery should restore room_info")
    
    print("✓ State recovery tests passed")
    tests_passed = tests_passed + 1
end

function run_all_tests()
    print("Running State Validation Tests...")
    print("================================")
    
    test_msdp_validation()
    test_toggle_validation()
    test_room_info_validation()
    test_state_recovery()
    
    print("\\nTest Results:")
    print("  Passed: " .. tests_passed)
    print("  Failed: " .. tests_failed)
    
    if tests_failed == 0 then
        print("\\n✅ All state validation tests passed!")
        return true
    else
        print("\\n❌ Some tests failed!")
        return false
    end
end

-- Execute tests
local success = run_all_tests()
if not success then
    os.exit(1)
end
'''

def test_state_validation():
    """Test the state validation implementation"""
    print("State Validation Test Suite")
    print("==========================")
    
    try:
        # Read the XML to extract the State Validator script
        with open('LuminariGUI.xml', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the State Validator script
        start_marker = '<name>State Validator</name>'
        end_marker = '</Script>'
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("❌ State Validator script not found in XML")
            return False
        
        script_start = content.find('<script>', start_idx) + 8
        script_end = content.find('</script>', script_start)
        
        if script_start == -1 or script_end == -1:
            print("❌ Could not extract State Validator script")
            return False
        
        state_validator_code = content[script_start:script_end]
        
        # Decode XML entities
        state_validator_code = state_validator_code.replace('&lt;', '<')
        state_validator_code = state_validator_code.replace('&gt;', '>')
        state_validator_code = state_validator_code.replace('&amp;', '&')
        state_validator_code = state_validator_code.replace('&quot;', '"')
        
        # Create test script with the validator and tests
        test_script = f'''
-- Initialize required globals for testing
GUI = GUI or {{}}
msdp = msdp or {{}}
map = map or {{}}

-- Mock functions that might not exist in test environment
function cecho(text) 
    print(text:gsub("<[^>]*>", ""))  -- Strip color codes for testing
end

function getMudletHomeDir()
    return "/tmp"
end

function io.exists(file)
    return false  -- For testing, assume files don't exist
end

function table.save(file, data)
    -- Mock save function
end

-- Load State Validator functions
{state_validator_code}

-- Test script
{create_test_lua_script()}
'''
        
        # Write to temporary file and test with Lua
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write(test_script)
            temp_file = f.name
        
        try:
            # Run with lua
            result = subprocess.run(['lua', temp_file], 
                                    capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ State validation tests passed")
                print("\nTest output:")
                print(result.stdout)
                return True
            else:
                print("❌ State validation tests failed")
                print("Error output:")
                print(result.stderr)
                print("Standard output:")
                print(result.stdout)
                return False
                
        finally:
            os.unlink(temp_file)
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except FileNotFoundError:
        print("❌ Lua interpreter not found - skipping state validation tests")
        return True  # Don't fail if lua is not available
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_state_validation()
    sys.exit(0 if success else 1)