#!/usr/bin/env python3
"""
Event System Testing for LuminariGUI
Tests event handlers and MSDP event processing with mocks.
"""

import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

class EventSystemTester:
    def __init__(self, xml_file="LuminariGUI.xml"):
        self.xml_file = xml_file
        self.lua_path = self._find_lua()
        self.test_results = []
        self.errors = []
        self.warnings = []
        self.event_handlers = []
        
    def _find_lua(self):
        """Find lua executable in system PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            for executable in ["lua", "lua5.1", "lua5.2", "lua5.3", "lua5.4", "luajit"]:
                full_path = os.path.join(path, executable)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
        return None
    
    def _extract_event_handlers(self):
        """Extract event handlers from XML scripts."""
        if not os.path.exists(self.xml_file):
            self.errors.append(f"XML file not found: {self.xml_file}")
            return []
        
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            self.errors.append(f"XML parsing error: {e}")
            return []
        
        handlers = []
        
        # Create a parent map for ElementTree compatibility
        parent_map = {c: p for p in root.iter() for c in p}
        
        # Find all <script> elements
        for script_elem in root.iter('script'):
            script_text = script_elem.text
            if script_text and script_text.strip():
                # Get parent context
                parent = parent_map.get(script_elem)
                if parent is not None:
                    name_elem = parent.find('name')
                    script_name = name_elem.text if name_elem is not None else "unnamed"
                else:
                    script_name = "unnamed"
                
                # Find event handler registrations
                event_handlers = self._parse_event_handlers(script_text, script_name)
                handlers.extend(event_handlers)
        
        return handlers
    
    def _parse_event_handlers(self, script_content, script_name):
        """Parse event handler registrations from script content."""
        handlers = []
        
        # Pattern for registerAnonymousEventHandler
        pattern = r'registerAnonymousEventHandler\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)'
        matches = re.finditer(pattern, script_content)
        
        for match in matches:
            event_name = match.group(1)
            handler_function = match.group(2)
            line_num = script_content[:match.start()].count('\n') + 1
            
            handlers.append({
                'event': event_name,
                'handler': handler_function,
                'script': script_name,
                'line': line_num
            })
        
        return handlers
    
    def _create_mudlet_mocks(self):
        """Create mock Mudlet functions for testing."""
        return '''
-- Mock Mudlet functions for testing
local event_handlers = {}
local timers = {}
local next_timer_id = 1
local raised_events = {}

function registerAnonymousEventHandler(event, handler_name)
    event_handlers[event] = event_handlers[event] or {}
    table.insert(event_handlers[event], handler_name)
    return #event_handlers[event]
end

function raiseEvent(event, ...)
    table.insert(raised_events, {event = event, args = {...}})
    if event_handlers[event] then
        for _, handler_name in ipairs(event_handlers[event]) do
            -- Resolve dotted handler names like "map.eventHandler"
            local handler = _G
            for part in string.gmatch(handler_name, "[^.]+") do
                handler = handler[part]
                if not handler then break end
            end
            if handler and type(handler) == "function" then
                handler(event, ...)
            end
        end
    end
end

function tempTimer(delay, code)
    local timer_id = next_timer_id
    next_timer_id = next_timer_id + 1
    timers[timer_id] = {delay = delay, code = code}
    return timer_id
end

function killTimer(timer_id)
    timers[timer_id] = nil
end

function cecho(text)
    -- Mock output
end

function decho(text)
    -- Mock output
end

function echo(text)
    -- Mock output
end

-- Keep native print for test output

-- Mock MSDP data
msdp = {
    ROOM = {
        VNUM = 1001,
        NAME = "Test Room",
        EXITS = {n = 1002, s = 1003},
        DOORS = {}
    },
    AFFECTS = {
        AFFECTED_BY = {"fly", "detect_invis"},
        SPELL_LIKE_AFFECTS = {
            {NAME = "bless", DURATION = 100, LOCATION = "all", TYPE = "spell", MODIFIER = "+1"}
        }
    },
    GROUP = {
        {NAME = "TestPlayer", HEALTH = 100, HEALTH_MAX = 100, MANA = 50, MANA_MAX = 50}
    },
    HEALTH = 100,
    HEALTH_MAX = 100,
    MANA = 50,
    MANA_MAX = 50,
    MOVEMENT = 100,
    MOVEMENT_MAX = 100,
    OPPONENT_HEALTH = 75,
    OPPONENT_HEALTH_MAX = 100,
    OPPONENT_NAME = "Test Enemy",
    CHARACTER_NAME = "TestPlayer",
    LEVEL = 10,
    CLASS = "warrior",
    POSITION = "standing"
}

-- Mock GUI globals
GUI = {
    toggles = {},
    tabbedInfoWindow = {},
    buttonWindow = {},
    group_data = {},
    castConsole = {},
    castConsoleTimer = nil
}

map = {
    room_info = {},
    aliases = {},
    eventHandler = function() end,
    onProtocolEnabled = function() end
}

-- Mock Geyser
Geyser = {
    Label = {
        new = function(params, parent)
            return {
                name = params.name,
                setStyleSheet = function() end,
                echo = function() end,
                show = function() end,
                hide = function() end
            }
        end
    }
}

-- Test utilities
function test_get_raised_events()
    return raised_events
end

function test_reset_events()
    raised_events = {}
end

function test_get_event_handlers()
    return event_handlers
end

function test_get_timers()
    return timers
end
'''
    
    def _create_event_test_cases(self):
        """Create test cases for event system."""
        return [
            {
                'name': 'msdp_room_event',
                'description': 'Test MSDP room event handling',
                'setup': '''
                    function map.eventHandler(event, ...)
                        if event == "msdp.ROOM" then
                            map.room_info = msdp.ROOM
                        end
                    end
                    
                    registerAnonymousEventHandler("msdp.ROOM", "map.eventHandler")
                ''',
                'test': '''
                    -- Trigger event
                    raiseEvent("msdp.ROOM")
                    
                    -- Verify handler was called
                    assert(map.room_info.VNUM == 1001, "Room VNUM should be set")
                    assert(map.room_info.NAME == "Test Room", "Room name should be set")
                '''
            },
            {
                'name': 'msdp_affects_event',
                'description': 'Test MSDP affects event handling',
                'setup': '''
                    function GUI.updateAffectIcons(event, ...)
                        if msdp.AFFECTS and msdp.AFFECTS.AFFECTED_BY then
                            GUI.current_affects = msdp.AFFECTS.AFFECTED_BY
                        end
                    end
                    
                    registerAnonymousEventHandler("msdp.AFFECTS", "GUI.updateAffectIcons")
                ''',
                'test': '''
                    -- Trigger event
                    raiseEvent("msdp.AFFECTS")
                    
                    -- Verify handler was called
                    assert(GUI.current_affects, "Affects should be set")
                    assert(#GUI.current_affects == 2, "Should have 2 affects")
                '''
            },
            {
                'name': 'timer_management',
                'description': 'Test timer creation and cleanup',
                'setup': '''
                    local test_timer = nil
                    
                    function create_test_timer()
                        test_timer = tempTimer(5, "test_timer_callback()")
                        return test_timer
                    end
                    
                    function cleanup_test_timer()
                        if test_timer then
                            killTimer(test_timer)
                            test_timer = nil
                        end
                    end
                ''',
                'test': '''
                    -- Create timer
                    local timer_id = create_test_timer()
                    assert(timer_id ~= nil, "Timer should be created")
                    
                    local timers = test_get_timers()
                    assert(timers[timer_id] ~= nil, "Timer should exist in registry")
                    
                    -- Cleanup timer
                    cleanup_test_timer()
                    timers = test_get_timers()
                    assert(timers[timer_id] == nil, "Timer should be cleaned up")
                '''
            },
            {
                'name': 'event_cascade',
                'description': 'Test event cascade handling',
                'setup': '''
                    local cascade_count = 0
                    
                    function handler1(event, ...)
                        cascade_count = cascade_count + 1
                        if cascade_count < 3 then
                            raiseEvent("test.cascade")
                        end
                    end
                    
                    function handler2(event, ...)
                        cascade_count = cascade_count + 10
                    end
                    
                    registerAnonymousEventHandler("test.cascade", "handler1")
                    registerAnonymousEventHandler("test.cascade", "handler2")
                ''',
                'test': '''
                    -- Trigger cascading event
                    raiseEvent("test.cascade")
                    
                    -- Verify cascade was handled correctly
                    assert(cascade_count == 33, "Cascade count should be 33 (1+10+1+10+1+10)")
                '''
            },
            {
                'name': 'error_handling',
                'description': 'Test error handling in event handlers',
                'setup': '''
                    local error_caught = false
                    
                    function error_handler(event, ...)
                        error("Test error")
                    end
                    
                    function safe_handler(event, ...)
                        local success, err = pcall(error_handler, event, ...)
                        if not success then
                            error_caught = true
                        end
                    end
                    
                    registerAnonymousEventHandler("test.error", "safe_handler")
                ''',
                'test': '''
                    -- Trigger error event
                    raiseEvent("test.error")
                    
                    -- Verify error was caught
                    assert(error_caught == true, "Error should be caught by pcall")
                '''
            }
        ]
    
    def _run_event_test(self, test_case):
        """Run a single event test case."""
        if not self.lua_path:
            self.errors.append("lua interpreter not found in PATH")
            return False
        
        # Create test Lua code
        lua_code = f'''
{self._create_mudlet_mocks()}

-- Test setup
{test_case['setup']}

-- Test execution
local function run_test()
{test_case['test']}
end

-- Run test with error handling
local success, err = pcall(run_test)
if success then
    print("PASS")
else
    print("FAIL: " .. tostring(err))
end
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as lua_file:
            lua_file.write(lua_code)
            lua_file_path = lua_file.name
        
        try:
            # Run lua interpreter
            result = subprocess.run(
                [self.lua_path, lua_file_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                return output == "PASS", output
            else:
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
        finally:
            # Clean up
            try:
                os.unlink(lua_file_path)
            except:
                pass
    
    def run_tests(self):
        """Run all event system tests."""
        print("Running event system tests...")
        
        if not self.lua_path:
            print("lua interpreter not found. Please install Lua:")
            print("  Ubuntu/Debian: sudo apt-get install lua5.1")
            print("  macOS: brew install lua")
            return False
        
        # Extract event handlers from XML
        handlers = self._extract_event_handlers()
        print(f"Found {len(handlers)} event handlers in XML")
        
        # Display handlers
        if handlers:
            print("\nEvent handlers found:")
            for handler in handlers:
                print(f"  {handler['event']} -> {handler['handler']} ({handler['script']})")
        
        # Run test cases
        test_cases = self._create_event_test_cases()
        
        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = 0
        
        print(f"\nRunning {total_tests} event system tests...")
        
        for test_case in test_cases:
            test_name = test_case['name']
            description = test_case['description']
            
            success, output = self._run_event_test(test_case)
            
            if success:
                passed_tests += 1
                print(f"  ✓ {test_name}: {description}")
            else:
                failed_tests += 1
                print(f"  ✗ {test_name}: {description} - {output}")
        
        # Summary
        print(f"\nEvent system test results:")
        print(f"  Event handlers found: {len(handlers)}")
        print(f"  Tests run: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        
        # Display errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
        
        return failed_tests == 0
    
    def get_results(self):
        """Get test results for integration."""
        return {
            'event_handlers': self.event_handlers,
            'test_results': self.test_results,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test event system in LuminariGUI')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    parser.add_argument('--list-handlers', action='store_true', help='List event handlers only')
    
    args = parser.parse_args()
    
    tester = EventSystemTester(args.xml)
    
    if args.list_handlers:
        handlers = tester._extract_event_handlers()
        print(f"Event handlers found in {args.xml}:")
        for handler in handlers:
            print(f"  {handler['event']} -> {handler['handler']} ({handler['script']}:{handler['line']})")
        return
    
    if args.quiet:
        # Suppress print statements
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = tester.run_tests()
    else:
        success = tester.run_tests()
    
    if not args.quiet and args.verbose:
        results = tester.get_results()
        print(f"\nDetailed results: {results}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()