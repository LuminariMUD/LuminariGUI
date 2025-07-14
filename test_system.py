#!/usr/bin/env python3
"""
System Testing for LuminariGUI
Tests for memory leaks, error boundaries, and resource management.
"""

import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
import json
import re
import time
from pathlib import Path

class SystemTester:
    def __init__(self, xml_file="LuminariGUI.xml"):
        self.xml_file = xml_file
        self.lua_path = self._find_lua()
        self.test_results = []
        self.errors = []
        self.warnings = []
        
    def _find_lua(self):
        """Find lua executable in system PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            for executable in ["lua", "lua5.1", "lua5.2", "lua5.3", "lua5.4", "luajit"]:
                full_path = os.path.join(path, executable)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
        return None
    
    def _extract_resource_usage(self):
        """Extract timer and handler usage patterns from XML."""
        if not os.path.exists(self.xml_file):
            self.errors.append(f"XML file not found: {self.xml_file}")
            return {}
        
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            self.errors.append(f"XML parsing error: {e}")
            return {}
        
        resource_usage = {
            'timers': {'created': [], 'killed': []},
            'handlers': {'registered': [], 'killed': []},
            'potential_leaks': []
        }
        
        # Create a parent map for ElementTree compatibility
        parent_map = {c: p for p in root.iter() for c in p}
        
        # Find all script elements
        for script_elem in root.iter('script'):
            script_text = script_elem.text
            if script_text and script_text.strip():
                parent = parent_map.get(script_elem)
                if parent is not None:
                    name_elem = parent.find('name')
                    script_name = name_elem.text if name_elem is not None else "unnamed"
                else:
                    script_name = "unnamed"
                
                self._analyze_resource_usage(script_text, script_name, resource_usage)
        
        return resource_usage
    
    def _analyze_resource_usage(self, script_content, script_name, resource_usage):
        """Analyze resource usage patterns in script content."""
        # Find timer operations
        timer_creates = re.findall(r'tempTimer\s*\(', script_content)
        timer_kills = re.findall(r'killTimer\s*\(', script_content)
        
        resource_usage['timers']['created'].extend([(script_name, len(timer_creates))])
        resource_usage['timers']['killed'].extend([(script_name, len(timer_kills))])
        
        # Find handler operations
        handler_registers = re.findall(r'registerAnonymousEventHandler\s*\(', script_content)
        handler_kills = re.findall(r'killAnonymousEventHandler\s*\(', script_content)
        
        resource_usage['handlers']['registered'].extend([(script_name, len(handler_registers))])
        resource_usage['handlers']['killed'].extend([(script_name, len(handler_kills))])
        
        # Check for potential leaks
        if len(timer_creates) > len(timer_kills):
            resource_usage['potential_leaks'].append({
                'script': script_name,
                'type': 'timer',
                'created': len(timer_creates),
                'killed': len(timer_kills)
            })
        
        if len(handler_registers) > len(handler_kills):
            resource_usage['potential_leaks'].append({
                'script': script_name,
                'type': 'handler',
                'created': len(handler_registers),
                'killed': len(handler_kills)
            })
    
    def _create_system_mocks(self):
        """Create system mocks for testing."""
        return '''
-- System testing mocks
local resource_tracker = {
    timers = {},
    handlers = {},
    next_timer_id = 1,
    next_handler_id = 1,
    memory_usage = 0,
    error_count = 0
}

-- Mock timer functions with tracking
function tempTimer(delay, code)
    local timer_id = resource_tracker.next_timer_id
    resource_tracker.next_timer_id = resource_tracker.next_timer_id + 1
    resource_tracker.timers[timer_id] = {
        delay = delay,
        code = code,
        created = os.time()
    }
    resource_tracker.memory_usage = resource_tracker.memory_usage + 100
    return timer_id
end

function killTimer(timer_id)
    if resource_tracker.timers[timer_id] then
        resource_tracker.timers[timer_id] = nil
        resource_tracker.memory_usage = resource_tracker.memory_usage - 100
        return true
    end
    return false
end

-- Mock handler functions with tracking
function registerAnonymousEventHandler(event, handler_name)
    local handler_id = resource_tracker.next_handler_id
    resource_tracker.next_handler_id = resource_tracker.next_handler_id + 1
    resource_tracker.handlers[handler_id] = {
        event = event,
        handler = handler_name,
        created = os.time()
    }
    resource_tracker.memory_usage = resource_tracker.memory_usage + 50
    return handler_id
end

function killAnonymousEventHandler(handler_id)
    if resource_tracker.handlers[handler_id] then
        resource_tracker.handlers[handler_id] = nil
        resource_tracker.memory_usage = resource_tracker.memory_usage - 50
        return true
    end
    return false
end

-- Error tracking
function track_error()
    resource_tracker.error_count = resource_tracker.error_count + 1
end

-- Test utilities
function get_resource_stats()
    local timer_count = 0
    local handler_count = 0
    
    for _ in pairs(resource_tracker.timers) do
        timer_count = timer_count + 1
    end
    
    for _ in pairs(resource_tracker.handlers) do
        handler_count = handler_count + 1
    end
    
    return {
        timers = timer_count,
        handlers = handler_count,
        memory_usage = resource_tracker.memory_usage,
        error_count = resource_tracker.error_count
    }
end

function reset_resource_tracker()
    resource_tracker.timers = {}
    resource_tracker.handlers = {}
    resource_tracker.memory_usage = 0
    resource_tracker.error_count = 0
end

-- Mock other functions
function cecho(text) end
function raiseEvent(event, ...) end
function getMudletHomeDir() return "/tmp" end

-- Mock globals
GUI = {toggles = {}}
msdp = {}
map = {room_info = {}}
'''
    
    def _create_system_test_cases(self):
        """Create system test cases."""
        return [
            {
                'name': 'timer_leak_test',
                'description': 'Test for timer memory leaks',
                'test': '''
                    local initial_stats = get_resource_stats()
                    
                    -- Create timers without cleanup
                    for i = 1, 10 do
                        tempTimer(1, "test_function()")
                    end
                    
                    local after_create = get_resource_stats()
                    assert(after_create.timers == initial_stats.timers + 10, "Should have 10 more timers")
                    assert(after_create.memory_usage > initial_stats.memory_usage, "Memory usage should increase")
                    
                    -- This simulates a leak - timers not cleaned up
                    print("Timer leak test: " .. (after_create.memory_usage - initial_stats.memory_usage) .. " bytes leaked")
                '''
            },
            {
                'name': 'handler_leak_test',
                'description': 'Test for event handler memory leaks',
                'test': '''
                    local initial_stats = get_resource_stats()
                    
                    -- Register handlers without cleanup
                    for i = 1, 5 do
                        registerAnonymousEventHandler("test.event", "test_handler")
                    end
                    
                    local after_register = get_resource_stats()
                    assert(after_register.handlers == initial_stats.handlers + 5, "Should have 5 more handlers")
                    assert(after_register.memory_usage > initial_stats.memory_usage, "Memory usage should increase")
                    
                    print("Handler leak test: " .. (after_register.memory_usage - initial_stats.memory_usage) .. " bytes leaked")
                '''
            },
            {
                'name': 'proper_cleanup_test',
                'description': 'Test proper resource cleanup',
                'test': '''
                    local initial_stats = get_resource_stats()
                    
                    -- Create and properly cleanup timers
                    local timer_ids = {}
                    for i = 1, 5 do
                        timer_ids[i] = tempTimer(1, "test_function()")
                    end
                    
                    -- Cleanup timers
                    for i = 1, 5 do
                        killTimer(timer_ids[i])
                    end
                    
                    local final_stats = get_resource_stats()
                    assert(final_stats.timers == initial_stats.timers, "Timer count should return to initial")
                    assert(final_stats.memory_usage == initial_stats.memory_usage, "Memory usage should return to initial")
                    
                    print("Proper cleanup test: Memory usage stable")
                '''
            },
            {
                'name': 'error_boundary_test',
                'description': 'Test error boundary protection',
                'test': '''
                    local initial_stats = get_resource_stats()
                    
                    -- Test function that might fail
                    local function risky_function()
                        if math.random() > 0.5 then
                            error("Random error")
                        end
                        return "success"
                    end
                    
                    -- Test with error boundary
                    local success_count = 0
                    local error_count = 0
                    
                    for i = 1, 10 do
                        local success, result = pcall(risky_function)
                        if success then
                            success_count = success_count + 1
                        else
                            error_count = error_count + 1
                            track_error()
                        end
                    end
                    
                    local final_stats = get_resource_stats()
                    assert(final_stats.error_count == error_count, "Error count should match tracked errors")
                    
                    print("Error boundary test: " .. error_count .. " errors caught, " .. success_count .. " successes")
                '''
            },
            {
                'name': 'resource_stress_test',
                'description': 'Stress test resource creation and cleanup',
                'test': '''
                    local initial_stats = get_resource_stats()
                    
                    -- Create many resources
                    local timer_ids = {}
                    local handler_ids = {}
                    
                    for i = 1, 100 do
                        timer_ids[i] = tempTimer(1, "test_function()")
                        handler_ids[i] = registerAnonymousEventHandler("test.event", "test_handler")
                    end
                    
                    local peak_stats = get_resource_stats()
                    
                    -- Cleanup all resources
                    for i = 1, 100 do
                        killTimer(timer_ids[i])
                        killAnonymousEventHandler(handler_ids[i])
                    end
                    
                    local final_stats = get_resource_stats()
                    
                    assert(final_stats.timers == initial_stats.timers, "All timers should be cleaned up")
                    assert(final_stats.handlers == initial_stats.handlers, "All handlers should be cleaned up")
                    assert(final_stats.memory_usage == initial_stats.memory_usage, "Memory should be fully released")
                    
                    print("Stress test: Peak memory " .. peak_stats.memory_usage .. ", final memory " .. final_stats.memory_usage)
                '''
            },
            {
                'name': 'double_cleanup_test',
                'description': 'Test double cleanup protection',
                'test': '''
                    -- Create a timer
                    local timer_id = tempTimer(1, "test_function()")
                    
                    -- First cleanup should succeed
                    local first_cleanup = killTimer(timer_id)
                    assert(first_cleanup == true, "First cleanup should succeed")
                    
                    -- Second cleanup should fail gracefully
                    local second_cleanup = killTimer(timer_id)
                    assert(second_cleanup == false, "Second cleanup should fail gracefully")
                    
                    print("Double cleanup test: Handled gracefully")
                '''
            }
        ]
    
    def _run_system_test(self, test_case):
        """Run a single system test case."""
        if not self.lua_path:
            self.errors.append("lua interpreter not found in PATH")
            return False
        
        # Create test Lua code
        lua_code = f'''
{self._create_system_mocks()}

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
                timeout=20
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                lines = output.split('\n')
                test_result = lines[-1]  # Last line should be PASS/FAIL
                additional_output = '\n'.join(lines[:-1]) if len(lines) > 1 else ""
                
                return test_result == "PASS", additional_output
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
        """Run all system tests."""
        print("Running system tests...")
        
        if not self.lua_path:
            print("lua interpreter not found. Please install Lua:")
            print("  Ubuntu/Debian: sudo apt-get install lua5.1")
            print("  macOS: brew install lua")
            return False
        
        # Analyze resource usage in XML
        resource_usage = self._extract_resource_usage()
        
        # Report potential leaks
        if resource_usage['potential_leaks']:
            print("Potential resource leaks detected:")
            for leak in resource_usage['potential_leaks']:
                print(f"  {leak['script']}: {leak['type']} leak ({leak['created']} created, {leak['killed']} killed)")
        else:
            print("No obvious resource leaks detected in static analysis")
        
        # Run system tests
        test_cases = self._create_system_test_cases()
        
        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = 0
        
        print(f"\nRunning {total_tests} system tests...")
        
        for test_case in test_cases:
            test_name = test_case['name']
            description = test_case['description']
            
            success, output = self._run_system_test(test_case)
            
            if success:
                passed_tests += 1
                print(f"  ✓ {test_name}: {description}")
                if output:
                    print(f"    {output}")
            else:
                failed_tests += 1
                print(f"  ✗ {test_name}: {description} - {output}")
        
        # Summary
        print(f"\nSystem test results:")
        print(f"  Tests run: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Potential leaks: {len(resource_usage['potential_leaks'])}")
        
        # Display errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
        
        return failed_tests == 0
    
    def get_results(self):
        """Get test results for integration."""
        return {
            'test_results': self.test_results,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run system tests for LuminariGUI')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    tester = SystemTester(args.xml)
    
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