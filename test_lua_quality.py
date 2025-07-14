#!/usr/bin/env python3
"""
Lua Quality Analysis for LuminariGUI
Static analysis using luacheck to find code quality issues.
"""

import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

class LuaQualityAnalyzer:
    def __init__(self, xml_file="LuminariGUI.xml"):
        self.xml_file = xml_file
        self.luacheck_path = self._find_luacheck()
        self.errors = []
        self.warnings = []
        self.issues = []
        
    def _find_luacheck(self):
        """Find luacheck executable in system PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            luacheck_path = os.path.join(path, "luacheck")
            if os.path.isfile(luacheck_path) and os.access(luacheck_path, os.X_OK):
                return luacheck_path
        return None
    
    def _extract_lua_scripts(self):
        """Extract all Lua script blocks from XML."""
        if not os.path.exists(self.xml_file):
            self.errors.append(f"XML file not found: {self.xml_file}")
            return []
        
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
        except ET.ParseError as e:
            self.errors.append(f"XML parsing error: {e}")
            return []
        
        scripts = []
        
        # Create a parent map for ElementTree compatibility
        parent_map = {c: p for p in root.iter() for c in p}
        
        # Find all <script> elements
        for script_elem in root.iter('script'):
            script_text = script_elem.text
            if script_text and script_text.strip():
                # Get parent context for better error reporting
                parent = parent_map.get(script_elem)
                if parent is not None:
                    name_elem = parent.find('name')
                    script_name = name_elem.text if name_elem is not None else "unnamed"
                else:
                    script_name = "unnamed"
                
                scripts.append({
                    'name': script_name,
                    'content': script_text,
                    'line': script_elem.sourceline if hasattr(script_elem, 'sourceline') else 0
                })
        
        return scripts
    
    def _get_luacheck_config(self):
        """Get the path to the luacheck configuration file."""
        # Check if custom config exists
        config_path = os.path.join("tests", "test_configs", "luacheck_config.lua")
        if os.path.exists(config_path):
            return config_path
        
        # Fallback to creating a temporary config
        self.warnings.append("Using fallback luacheck configuration. Consider using tests/test_configs/luacheck_config.lua")
        config_content = """
-- Fallback Mudlet/LuminariGUI configuration
std = "luajit"
globals = {
    "cecho", "decho", "echo", "send",
    "raiseEvent", "registerAnonymousEventHandler",
    "msdp", "gmcp", "mud", "matches",
    "Geyser", "geyser",
    "GUI", "LUM", "map", "demonnic"
}
ignore = {
    "212", "213", "311", "411", "412", "421", "422", "542", "614"
}
"""
        
        config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.luacheckrc', delete=False)
        config_file.write(config_content)
        config_file.close()
        return config_file.name
    
    def _analyze_script(self, script_name, script_content):
        """Analyze a single Lua script with luacheck."""
        if not self.luacheck_path:
            self.errors.append("luacheck not found in PATH. Please install luacheck.")
            return False
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as script_file:
            script_file.write(script_content)
            script_file_path = script_file.name
        
        config_file_path = self._get_luacheck_config()
        
        try:
            # Run luacheck without JSON formatter (use default output)
            result = subprocess.run(
                [self.luacheck_path, '--config', config_file_path, script_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # No issues found
                return True
            elif result.returncode == 1:
                # Issues found, parse default output
                # Default luacheck output format:
                # filename:line:column: message
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line and not line.startswith('Checking') and not line.startswith('Total:'):
                        # Parse line like: test.lua:3:5: setting non-standard global variable 'unused_global'
                        match = re.match(r'^\s*([^:]+):(\d+):(\d+):\s*(.+)$', line)
                        if match:
                            _, line_num, col_num, message = match.groups()
                            # Determine severity based on message content
                            if 'error' in message.lower():
                                severity = 'error'
                                code = 'E'
                            else:
                                severity = 'warning'
                                code = 'W'
                            
                            self.issues.append({
                                'script': script_name,
                                'line': int(line_num),
                                'column': int(col_num),
                                'code': code,
                                'message': message.strip(),
                                'severity': severity
                            })
                return False
            else:
                # luacheck error
                self.errors.append(f"luacheck error for '{script_name}': {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.errors.append(f"Timeout analyzing script '{script_name}'")
            return False
        except Exception as e:
            self.errors.append(f"Error analyzing script '{script_name}': {e}")
            return False
        finally:
            # Clean up temporary files
            try:
                os.unlink(script_file_path)
                # Only delete config if it's a temporary file
                if config_file_path and not config_file_path.endswith("luacheck_config.lua"):
                    os.unlink(config_file_path)
            except:
                pass
    
    def _categorize_issues(self):
        """Categorize issues by severity and type."""
        categorized = {
            'critical': [],
            'errors': [],
            'warnings': [],
            'style': []
        }
        
        for issue in self.issues:
            code = issue['code']
            severity = issue['severity']
            
            # Critical issues (undefined access)
            if code in ['111', '112', '113', '142', '143', '321']:
                categorized['critical'].append(issue)
            # Errors (logic problems)
            elif code in ['511', '512', '521', '531', '541']:
                categorized['errors'].append(issue)
            # Warnings (potential issues)
            elif code in ['311', '312', '551']:
                categorized['warnings'].append(issue)
            # Style issues
            elif code in ['611', '612', '613', '631']:
                categorized['style'].append(issue)
            else:
                # Default to warnings
                categorized['warnings'].append(issue)
        
        return categorized
    
    def run_analysis(self):
        """Run quality analysis on all scripts."""
        print("Running Lua quality analysis...")
        
        if not self.luacheck_path:
            print("luacheck not found. Please install luacheck:")
            print("  Ubuntu/Debian: sudo apt-get install luacheck")
            print("  macOS: brew install luacheck")
            print("  Other: luarocks install luacheck")
            return False
        
        # Extract scripts from XML
        scripts = self._extract_lua_scripts()
        if not scripts:
            if not self.errors:
                self.warnings.append("No Lua scripts found in XML file")
            return False
        
        print(f"Found {len(scripts)} Lua scripts to analyze")
        
        # Analyze each script
        passed = 0
        failed = 0
        
        for script in scripts:
            if self._analyze_script(script['name'], script['content']):
                passed += 1
                print(f"✓ {script['name']}")
            else:
                failed += 1
                print(f"⚠ {script['name']}")
        
        # Categorize and display results
        categorized = self._categorize_issues()
        
        print(f"\nQuality analysis results:")
        print(f"  Scripts analyzed: {len(scripts)}")
        print(f"  Clean scripts: {passed}")
        print(f"  Scripts with issues: {failed}")
        print(f"  Total issues: {len(self.issues)}")
        
        # Display issues by category
        for category, issues in categorized.items():
            if issues:
                print(f"\n{category.upper()} ({len(issues)} issues):")
                for issue in issues:
                    print(f"  {issue['script']}:{issue['line']}:{issue['column']} - {issue['message']}")
        
        # Display errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
        
        return len(categorized['critical']) == 0 and len(categorized['errors']) == 0
    
    def get_results(self):
        """Get analysis results for integration with other tools."""
        categorized = self._categorize_issues()
        return {
            'passed': len(categorized['critical']) == 0 and len(categorized['errors']) == 0,
            'issues': categorized,
            'total_issues': len(self.issues),
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Lua code quality in LuminariGUI XML')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to analyze')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings too')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode - only errors')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    args = parser.parse_args()
    
    analyzer = LuaQualityAnalyzer(args.xml)
    
    if args.quiet:
        # Suppress print statements
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = analyzer.run_analysis()
    else:
        success = analyzer.run_analysis()
    
    if args.json:
        results = analyzer.get_results()
        print(json.dumps(results, indent=2))
    
    if not args.quiet and args.verbose:
        results = analyzer.get_results()
        print(f"\nDetailed results: {results}")
    
    # Apply strict mode
    if args.strict:
        results = analyzer.get_results()
        success = success and results['total_issues'] == 0
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()