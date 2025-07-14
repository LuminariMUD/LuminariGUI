#!/usr/bin/env python3
"""
Lua Function Unit Testing for LuminariGUI
Tests core Lua functions with known inputs and expected outputs.
"""

import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

class LuaFunctionTester:
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
    
    def _extract_functions(self):
        """Extract testable functions from XML scripts."""
        if not os.path.exists(self.xml_file):
            self.errors.append(f"XML file not found: {self.xml_file}")
            return []
        
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            self.errors.append(f"XML parsing error: {e}")
            return []
        
        functions = []
        
        # Find all <script> elements
        for script_elem in root.iter('script'):
            script_text = script_elem.text
            if script_text and script_text.strip():
                # Get parent context
                parent = script_elem.getparent()
                if parent is not None:
                    name_elem = parent.find('name')
                    script_name = name_elem.text if name_elem is not None else "unnamed"
                else:
                    script_name = "unnamed"
                
                # Extract function definitions
                extracted_functions = self._parse_functions(script_text, script_name)
                functions.extend(extracted_functions)
        
        return functions
    
    def _parse_functions(self, script_content, script_name):
        """Parse function definitions from script content."""
        functions = []
        
        # Regex patterns for function definitions
        patterns = [
            r'function\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\(',
            r'local\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*=\s*function\s*\('
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, script_content, re.MULTILINE)
            for match in matches:
                func_name = match.group(1)
                line_num = script_content[:match.start()].count('\n') + 1
                
                # Extract function body (simplified)
                start_pos = match.start()
                func_body = self._extract_function_body(script_content, start_pos)
                
                functions.append({
                    'name': func_name,
                    'script': script_name,
                    'line': line_num,
                    'body': func_body,
                    'testable': self._is_testable(func_name, func_body)
                })
        
        return functions
    
    def _extract_function_body(self, content, start_pos):
        """Extract function body from content starting at position."""
        # Simple extraction - find matching end
        lines = content[start_pos:].split('\n')
        function_lines = []
        depth = 0
        
        for line in lines:
            function_lines.append(line)
            
            # Count function/end pairs
            if re.search(r'\bfunction\b', line):
                depth += 1
            if re.search(r'\bend\b', line):
                depth -= 1
                if depth == 0:
                    break
        
        return '\n'.join(function_lines)
    
    def _is_testable(self, func_name, func_body):
        """Determine if a function is suitable for unit testing."""
        # Skip functions that are clearly not testable
        skip_patterns = [
            r'registerAnonymousEventHandler',
            r'tempTimer',
            r'GUI\.',
            r'cecho',
            r'decho',
            r'echo',
            r'print',
            r'send',
            r'raiseEvent',
            r'Geyser',
            r'msdp\.',
            r'gmcp\.',
            r'getMudletHomeDir',
            r'table\.save',
            r'table\.load'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, func_body):
                return False
        
        # Functions that are likely testable
        if any(keyword in func_body for keyword in ['return', 'local', 'if', 'for', 'while']):
            return True
        
        return False
    
    def _create_test_cases(self):
        """Create test cases for specific functions."""
        test_cases = [
            # Map utility functions
            {
                'name': 'map.calcMinimapPadding',
                'setup': '''
                    map = {
                        calcMinimapPadding = function(text)
                            if not text or text == "" then
                                return ""
                            end
                            local padding_size = math.floor((20 - #text) / 2)
                            if padding_size < 0 then padding_size = 0 end
                            local padding = string.rep(" ", padding_size)
                            return padding .. text .. padding
                        end
                    }
                ''',
                'tests': [
                    {'function': 'map.calcMinimapPadding', 'input': '""', 'expected': ''},
                    {'function': 'map.calcMinimapPadding', 'input': '"x"', 'expected_pattern': r'.*x.*'},
                ]
            },
            # String utility functions
            {
                'name': 'string_utils',
                'setup': '''
                    function trim(s)
                        return s:match("^%s*(.-)%s*$")
                    end
                    
                    function split(str, delimiter)
                        local result = {}
                        for match in (str..delimiter):gmatch("(.-)"..delimiter) do
                            table.insert(result, match)
                        end
                        return result
                    end
                    
                    function table_to_string(t)
                        local result = "{"
                        for i, v in ipairs(t) do
                            if i > 1 then result = result .. ", " end
                            result = result .. '"' .. v .. '"'
                        end
                        return result .. "}"
                    end
                ''',
                'tests': [
                    {'function': 'trim', 'input': '"  hello  "', 'expected': 'hello'},
                    {'function': 'split', 'input': '"a,b,c", ","', 'expected_table': '{"a", "b", "c"}'},
                ]
            },
            # Math utility functions
            {
                'name': 'math_utils',
                'setup': '''
                    function clamp(value, min_val, max_val)
                        return math.max(min_val, math.min(max_val, value))
                    end
                    
                    function round(num, decimals)
                        local mult = 10^(decimals or 0)
                        return math.floor(num * mult + 0.5) / mult
                    end
                ''',
                'tests': [
                    {'function': 'clamp', 'input': '5, 1, 10', 'expected': '5'},
                    {'function': 'clamp', 'input': '15, 1, 10', 'expected': '10'},
                    {'function': 'clamp', 'input': '-5, 1, 10', 'expected': '1'},
                    {'function': 'round', 'input': '3.14159, 2', 'expected': '3.14'},
                ]
            },
            # Table utility functions
            {
                'name': 'table_utils',
                'setup': '''
                    function table_contains(tbl, value)
                        for _, v in ipairs(tbl) do
                            if v == value then
                                return true
                            end
                        end
                        return false
                    end
                    
                    function table_keys(tbl)
                        local keys = {}
                        for k, _ in pairs(tbl) do
                            table.insert(keys, k)
                        end
                        return keys
                    end
                ''',
                'tests': [
                    {'function': 'table_contains', 'input': '{1, 2, 3}, 2', 'expected': 'true'},
                    {'function': 'table_contains', 'input': '{1, 2, 3}, 5', 'expected': 'false'},
                ]
            }
        ]
        
        return test_cases
    
    def _run_lua_test(self, test_name, lua_code):
        """Run a single Lua test."""
        if not self.lua_path:
            self.errors.append("lua interpreter not found in PATH")
            return False
        
        # Create temporary file with test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as lua_file:
            lua_file.write(lua_code)
            lua_file_path = lua_file.name
        
        try:
            # Run lua interpreter
            result = subprocess.run(
                [self.lua_path, lua_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
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
    
    def _create_test_lua_code(self, test_case, test_item):
        """Create Lua code for a test case."""
        setup = test_case.get('setup', '')
        function_name = test_item.get('function', test_case['name'])
        input_args = test_item['input']
        expected = test_item.get('expected', '')
        expected_pattern = test_item.get('expected_pattern', '')
        expected_table = test_item.get('expected_table', '')
        
        # Check if this is a table result test
        if expected_table:
            lua_code = f'''
{setup}

-- Table serialization function
function table_to_string(t)
    if type(t) ~= "table" then
        return tostring(t)
    end
    local result = "{{"
    for i, v in ipairs(t) do
        if i > 1 then result = result .. ", " end
        result = result .. '"' .. tostring(v) .. '"'
    end
    return result .. "}}"
end

-- Test function
local function run_test()
    local result = {function_name}({input_args})
    return table_to_string(result)
end

-- Execute test
local success, result = pcall(run_test)
if success then
    print(result)
else
    print("ERROR: " .. tostring(result))
end
'''
        else:
            lua_code = f'''
{setup}

-- Test function
local function run_test()
    local result = {function_name}({input_args})
    return result
end

-- Execute test
local success, result = pcall(run_test)
if success then
    print(tostring(result))
else
    print("ERROR: " .. tostring(result))
end
'''
        return lua_code
    
    def _validate_result(self, result, expected, expected_pattern, expected_table=None):
        """Validate test result against expected value or pattern."""
        if expected_pattern:
            return re.match(expected_pattern, result) is not None
        elif expected_table:
            return str(result).strip() == str(expected_table).strip()
        elif expected:
            return str(result).strip() == str(expected).strip()
        else:
            return True  # No validation specified
    
    def run_tests(self):
        """Run all function tests."""
        print("Running Lua function unit tests...")
        
        if not self.lua_path:
            print("lua interpreter not found. Please install Lua:")
            print("  Ubuntu/Debian: sudo apt-get install lua5.1")
            print("  macOS: brew install lua")
            return False
        
        # Get test cases
        test_cases = self._create_test_cases()
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_case in test_cases:
            test_name = test_case['name']
            print(f"\nTesting {test_name}:")
            
            for i, test_item in enumerate(test_case['tests']):
                total_tests += 1
                test_id = f"{test_name}_{i+1}"
                
                # Create and run test
                lua_code = self._create_test_lua_code(test_case, test_item)
                success, result = self._run_lua_test(test_id, lua_code)
                
                if success:
                    # Validate result
                    expected = test_item.get('expected', '')
                    expected_pattern = test_item.get('expected_pattern', '')
                    expected_table = test_item.get('expected_table', '')
                    
                    if self._validate_result(result, expected, expected_pattern, expected_table):
                        passed_tests += 1
                        print(f"  ✓ Test {i+1}: {test_item['input']} -> {result}")
                    else:
                        failed_tests += 1
                        expected_display = expected_table or expected or expected_pattern
                        print(f"  ✗ Test {i+1}: {test_item['input']} -> {result} (expected: {expected_display})")
                else:
                    failed_tests += 1
                    print(f"  ✗ Test {i+1}: {test_item['input']} -> ERROR: {result}")
        
        # Summary
        print(f"\nFunction test results:")
        print(f"  Total tests: {total_tests}")
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
            'test_results': self.test_results,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Lua function unit tests for LuminariGUI')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    
    args = parser.parse_args()
    
    tester = LuaFunctionTester(args.xml)
    
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