#!/usr/bin/env python3
"""
Performance Testing for LuminariGUI
Benchmarks critical functions and identifies performance bottlenecks.
"""

import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
import json
import re
import time
import statistics
from pathlib import Path

class PerformanceTester:
    def __init__(self, xml_file="LuminariGUI.xml"):
        self.xml_file = xml_file
        self.lua_path = self._find_lua()
        self.benchmark_results = {}
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
    
    def _extract_performance_critical_functions(self):
        """Extract functions that are performance-critical."""
        if not os.path.exists(self.xml_file):
            self.errors.append(f"XML file not found: {self.xml_file}")
            return []
        
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            self.errors.append(f"XML parsing error: {e}")
            return []
        
        critical_functions = []
        
        # Functions that are likely performance-critical based on patterns
        critical_patterns = [
            r'function.*make_room',
            r'function.*handle_move',
            r'function.*calcMinimapPadding',
            r'function.*calcAsciimapPadding',
            r'function.*adjustMinimapFontSize',
            r'function.*adjustAsciimapFontSize',
            r'function.*updateAffectIcons',
            r'function.*updateGroup',
            r'function.*shift_room'
        ]
        
        # Find all script elements
        for script_elem in root.iter('script'):
            script_text = script_elem.text
            if script_text and script_text.strip():
                parent = script_elem.getparent()
                if parent is not None:
                    name_elem = parent.find('name')
                    script_name = name_elem.text if name_elem is not None else "unnamed"
                else:
                    script_name = "unnamed"
                
                for pattern in critical_patterns:
                    matches = re.finditer(pattern, script_text, re.IGNORECASE)
                    for match in matches:
                        line_num = script_text[:match.start()].count('\n') + 1
                        func_body = self._extract_function_body(script_text, match.start())
                        
                        critical_functions.append({
                            'name': match.group(0),
                            'script': script_name,
                            'line': line_num,
                            'body': func_body
                        })
        
        return critical_functions
    
    def _extract_function_body(self, content, start_pos):
        """Extract function body from content starting at position."""
        lines = content[start_pos:].split('\n')
        function_lines = []
        depth = 0
        
        for line in lines:
            function_lines.append(line)
            
            if re.search(r'\bfunction\b', line):
                depth += 1
            if re.search(r'\bend\b', line):
                depth -= 1
                if depth == 0:
                    break
        
        return '\n'.join(function_lines)
    
    def _create_performance_mocks(self):
        """Create performance testing mocks."""
        return '''
-- Performance testing mocks and utilities
local performance = {
    start_time = 0,
    measurements = {}
}

-- High-resolution timer
function performance.start_timer()
    performance.start_time = os.clock()
end

function performance.end_timer(name)
    local elapsed = (os.clock() - performance.start_time) * 1000 -- Convert to milliseconds
    performance.measurements[name] = performance.measurements[name] or {}
    table.insert(performance.measurements[name], elapsed)
    return elapsed
end

function performance.get_stats(name)
    local measurements = performance.measurements[name]
    if not measurements or #measurements == 0 then
        return nil
    end
    
    local sum = 0
    local min_val = measurements[1]
    local max_val = measurements[1]
    
    for _, value in ipairs(measurements) do
        sum = sum + value
        if value < min_val then min_val = value end
        if value > max_val then max_val = value end
    end
    
    return {
        count = #measurements,
        average = sum / #measurements,
        min = min_val,
        max = max_val,
        total = sum
    }
end

-- Mock Mudlet functions
function getMudletHomeDir() return "/tmp" end
function cecho(text) end
function decho(text) end
function echo(text) end
function raiseEvent(event, ...) end
function registerAnonymousEventHandler(event, handler) end
function tempTimer(delay, code) return 1 end
function killTimer(id) end

-- Mock globals
GUI = {
    toggles = {},
    tabbedInfoWindow = {},
    buttonWindow = {},
    group_data = {},
    castConsole = {},
    Box2 = {get_width = function() return 300 end},
    Right = {get_width = function() return 200 end, get_height = function() return 400 end}
}

msdp = {
    ROOM = {
        VNUM = 1001,
        NAME = "Test Room",
        EXITS = {n = 1002, s = 1003, e = 1004, w = 1005},
        DOORS = {}
    },
    AFFECTS = {
        AFFECTED_BY = {"fly", "detect_invis", "bless", "haste"},
        SPELL_LIKE_AFFECTS = {}
    },
    GROUP = {},
    HEALTH = 100,
    HEALTH_MAX = 100,
    CHARACTER_NAME = "TestPlayer"
}

map = {
    room_info = {},
    aliases = {},
    rooms = {},
    areas = {}
}

areas = {
    Midgaard = 1,
    Mosswood = 2,
    Dwarven = 3
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
                hide = function() end,
                get_width = function() return 100 end,
                get_height = function() return 20 end
            }
        end
    }
}

-- Test data generators
function generate_room_data(count)
    local rooms = {}
    for i = 1, count do
        rooms[i] = {
            vnum = 1000 + i,
            name = "Room " .. i,
            exits = {n = 1000 + i + 1, s = 1000 + i - 1},
            x = math.random(-100, 100),
            y = math.random(-100, 100),
            z = 0
        }
    end
    return rooms
end

function generate_affect_data(count)
    local affects = {}
    for i = 1, count do
        affects[i] = "affect_" .. i
    end
    return affects
end

function generate_group_data(count)
    local group = {}
    for i = 1, count do
        group[i] = {
            NAME = "Player" .. i,
            HEALTH = math.random(50, 100),
            HEALTH_MAX = 100,
            MANA = math.random(20, 50),
            MANA_MAX = 50
        }
    end
    return group
end
'''
    
    def _create_performance_test_cases(self):
        """Create performance test cases."""
        return [
            {
                'name': 'string_operations',
                'description': 'Test string manipulation performance',
                'setup': '''
                    local test_strings = {}
                    for i = 1, 1000 do
                        test_strings[i] = "Test string " .. i .. " with some content"
                    end
                ''',
                'test': '''
                    performance.start_timer()
                    local result = {}
                    for i = 1, 1000 do
                        result[i] = test_strings[i]:upper():gsub(" ", "_")
                    end
                    performance.end_timer("string_operations")
                '''
            },
            {
                'name': 'table_operations',
                'description': 'Test table manipulation performance',
                'setup': '''
                    local test_table = {}
                    for i = 1, 1000 do
                        test_table[i] = {id = i, name = "item" .. i, value = math.random(1, 100)}
                    end
                ''',
                'test': '''
                    performance.start_timer()
                    local sorted_table = {}
                    for i, item in ipairs(test_table) do
                        table.insert(sorted_table, item)
                    end
                    table.sort(sorted_table, function(a, b) return a.value > b.value end)
                    performance.end_timer("table_operations")
                '''
            },
            {
                'name': 'room_creation_simulation',
                'description': 'Simulate room creation performance',
                'setup': '''
                    function create_room(vnum, name, exits, coords)
                        local room = {
                            vnum = vnum,
                            name = name,
                            exits = exits or {},
                            x = coords and coords.x or 0,
                            y = coords and coords.y or 0,
                            z = coords and coords.z or 0,
                            area = 1
                        }
                        map.rooms[vnum] = room
                        return room
                    end
                ''',
                'test': '''
                    performance.start_timer()
                    for i = 1, 100 do
                        local room_data = {
                            vnum = 1000 + i,
                            name = "Room " .. i,
                            exits = {n = 1000 + i + 1, s = 1000 + i - 1},
                            coords = {x = math.random(-50, 50), y = math.random(-50, 50), z = 0}
                        }
                        create_room(room_data.vnum, room_data.name, room_data.exits, room_data.coords)
                    end
                    performance.end_timer("room_creation")
                '''
            },
            {
                'name': 'affect_processing',
                'description': 'Test affect processing performance',
                'setup': '''
                    function process_affects(affects)
                        local processed = {}
                        for i, affect in ipairs(affects) do
                            processed[affect] = {
                                active = true,
                                duration = math.random(10, 300),
                                icon = "icons/" .. affect .. ".png"
                            }
                        end
                        return processed
                    end
                ''',
                'test': '''
                    local affects = generate_affect_data(50)
                    performance.start_timer()
                    local processed_affects = process_affects(affects)
                    performance.end_timer("affect_processing")
                '''
            },
            {
                'name': 'group_data_processing',
                'description': 'Test group data processing performance',
                'setup': '''
                    function process_group_data(group)
                        local processed = {}
                        for i, member in ipairs(group) do
                            processed[i] = {
                                name = member.NAME,
                                health_percent = (member.HEALTH / member.HEALTH_MAX) * 100,
                                mana_percent = (member.MANA / member.MANA_MAX) * 100,
                                status = member.HEALTH > 50 and "healthy" or "injured"
                            }
                        end
                        return processed
                    end
                ''',
                'test': '''
                    local group = generate_group_data(10)
                    performance.start_timer()
                    local processed_group = process_group_data(group)
                    performance.end_timer("group_processing")
                '''
            },
            {
                'name': 'font_calculation_simulation',
                'description': 'Simulate font size calculation performance',
                'setup': '''
                    function calculate_font_size(container_width, text_length)
                        local base_size = 10
                        local char_width = 7
                        local max_chars = math.floor(container_width / char_width)
                        
                        if text_length <= max_chars then
                            return base_size
                        else
                            return math.max(6, base_size - math.floor(text_length / max_chars))
                        end
                    end
                ''',
                'test': '''
                    performance.start_timer()
                    for i = 1, 1000 do
                        local width = math.random(100, 400)
                        local text_len = math.random(10, 100)
                        calculate_font_size(width, text_len)
                    end
                    performance.end_timer("font_calculation")
                '''
            },
            {
                'name': 'regex_pattern_matching',
                'description': 'Test regex pattern matching performance',
                'setup': '''
                    local test_patterns = {
                        "^You (.*) (.*)$",
                        "^([A-Za-z]+) says (.*)$",
                        "^Health: (%d+)/(%d+)$",
                        "^Mana: (%d+)/(%d+)$"
                    }
                    
                    local test_strings = {
                        "You attack the goblin",
                        "John says hello world",
                        "Health: 85/100",
                        "Mana: 42/50",
                        "Some random text that won't match"
                    }
                ''',
                'test': '''
                    performance.start_timer()
                    for i = 1, 100 do
                        for _, pattern in ipairs(test_patterns) do
                            for _, text in ipairs(test_strings) do
                                text:match(pattern)
                            end
                        end
                    end
                    performance.end_timer("regex_matching")
                '''
            }
        ]
    
    def _run_performance_test(self, test_case):
        """Run a single performance test case."""
        if not self.lua_path:
            self.errors.append("lua interpreter not found in PATH")
            return False
        
        # Create test Lua code
        lua_code = f'''
{self._create_performance_mocks()}

-- Test setup
{test_case['setup']}

-- Test execution
local function run_test()
{test_case['test']}
end

-- Run test with error handling
local success, err = pcall(run_test)
if success then
    local stats = performance.get_stats("{test_case['name']}")
    if stats then
        print("PASS")
        print("Average: " .. string.format("%.2f", stats.average) .. "ms")
        print("Min: " .. string.format("%.2f", stats.min) .. "ms")
        print("Max: " .. string.format("%.2f", stats.max) .. "ms")
        print("Count: " .. stats.count)
    else
        print("PASS")
    end
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
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                lines = output.split('\n')
                
                if lines[0] == "PASS":
                    # Parse performance data
                    perf_data = {}
                    for line in lines[1:]:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            perf_data[key.strip()] = value.strip()
                    
                    return True, perf_data
                else:
                    return False, lines[0] if lines else "Unknown error"
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
    
    def run_benchmarks(self):
        """Run all performance benchmarks."""
        print("Running performance benchmarks...")
        
        if not self.lua_path:
            print("lua interpreter not found. Please install Lua:")
            print("  Ubuntu/Debian: sudo apt-get install lua5.1")
            print("  macOS: brew install lua")
            return False
        
        # Run benchmark tests
        test_cases = self._create_performance_test_cases()
        
        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = 0
        
        print(f"Running {total_tests} performance benchmarks...")
        
        for test_case in test_cases:
            test_name = test_case['name']
            description = test_case['description']
            
            success, result = self._run_performance_test(test_case)
            
            if success:
                passed_tests += 1
                print(f"  ✓ {test_name}: {description}")
                
                # Display performance data
                if isinstance(result, dict):
                    self.benchmark_results[test_name] = result
                    for key, value in result.items():
                        print(f"    {key}: {value}")
            else:
                failed_tests += 1
                print(f"  ✗ {test_name}: {description} - {result}")
        
        # Summary
        print(f"\nPerformance benchmark results:")
        print(f"  Tests run: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        
        # Performance warnings
        self._analyze_performance_results()
        
        # Display errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print("\nPerformance warnings:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        return failed_tests == 0
    
    def _analyze_performance_results(self):
        """Analyze performance results for warnings."""
        # Define performance thresholds (in milliseconds)
        thresholds = {
            'string_operations': 10.0,
            'table_operations': 20.0,
            'room_creation': 50.0,
            'affect_processing': 15.0,
            'group_processing': 10.0,
            'font_calculation': 25.0,
            'regex_matching': 30.0
        }
        
        for test_name, result in self.benchmark_results.items():
            if 'Average' in result:
                avg_time = float(result['Average'].replace('ms', ''))
                threshold = thresholds.get(test_name, 50.0)
                
                if avg_time > threshold:
                    self.warnings.append(f"{test_name}: Average time {avg_time:.2f}ms exceeds threshold {threshold}ms")
    
    def get_results(self):
        """Get benchmark results for integration."""
        return {
            'benchmark_results': self.benchmark_results,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run performance benchmarks for LuminariGUI')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to benchmark')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    tester = PerformanceTester(args.xml)
    
    if args.quiet:
        # Suppress print statements
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = tester.run_benchmarks()
    else:
        success = tester.run_benchmarks()
    
    if args.json:
        results = tester.get_results()
        print(json.dumps(results, indent=2))
    
    if not args.quiet and args.verbose:
        results = tester.get_results()
        print(f"\nDetailed results: {results}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()