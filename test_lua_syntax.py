#!/usr/bin/env python3
"""
Lua Syntax Testing for LuminariGUI
Validates Lua code syntax using luac compiler before package creation.
"""

import os
import sys
import tempfile
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

class LuaSyntaxTester:
    def __init__(self, xml_file="LuminariGUI.xml"):
        self.xml_file = xml_file
        self.luac_path = self._find_luac()
        self.errors = []
        self.warnings = []
        
    def _find_luac(self):
        """Find luac executable in system PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            for executable in ["luac", "luac5.1", "luac5.2", "luac5.3", "luac5.4"]:
                full_path = os.path.join(path, executable)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
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
    
    def _validate_script_syntax(self, script_name, script_content):
        """Validate syntax of a single Lua script."""
        if not self.luac_path:
            self.errors.append(f"luac not found in PATH. Please install Lua compiler.")
            return False
        
        # Create temporary file for luac
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as tmp_file:
            tmp_file.write(script_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Run luac -p (parse only) to check syntax
            result = subprocess.run(
                [self.luac_path, '-p', tmp_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True
            else:
                # Parse luac error output
                error_msg = result.stderr.strip()
                # Remove temporary file path from error message
                error_msg = error_msg.replace(tmp_file_path, f"<{script_name}>")
                self.errors.append(f"Syntax error in '{script_name}': {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            self.errors.append(f"Timeout validating script '{script_name}'")
            return False
        except Exception as e:
            self.errors.append(f"Error validating script '{script_name}': {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    def _check_common_issues(self, scripts):
        """Check for common Lua issues in the codebase."""
        issues_found = []
        
        for script in scripts:
            content = script['content']
            name = script['name']
            
            # Check for common issues
            if 'function(' in content:
                issues_found.append(f"Warning in '{name}': Missing space after 'function' keyword")
            
            if 'end)' in content and 'end );' not in content:
                issues_found.append(f"Warning in '{name}': 'end)' pattern may indicate missing semicolon")
            
            # Check for HTML entities that should be unescaped
            if '&lt;' in content or '&gt;' in content or '&amp;' in content:
                issues_found.append(f"Warning in '{name}': HTML entities found - may need unescaping")
            
            # Check for potential global variable issues
            if 'GUI.' in content and 'local GUI' not in content:
                # This is expected in this codebase, so it's just informational
                pass
        
        return issues_found
    
    def run_tests(self):
        """Run all syntax tests and return results."""
        print("Running Lua syntax validation...")
        
        # Extract scripts from XML
        scripts = self._extract_lua_scripts()
        if not scripts:
            if not self.errors:
                self.warnings.append("No Lua scripts found in XML file")
            return False
        
        print(f"Found {len(scripts)} Lua scripts to validate")
        
        # Check syntax of each script
        passed = 0
        failed = 0
        
        for script in scripts:
            if self._validate_script_syntax(script['name'], script['content']):
                passed += 1
                print(f"✓ {script['name']}")
            else:
                failed += 1
                print(f"✗ {script['name']}")
        
        # Check for common issues
        common_issues = self._check_common_issues(scripts)
        self.warnings.extend(common_issues)
        
        # Print summary
        print(f"\nSyntax validation results:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Warnings: {len(self.warnings)}")
        
        # Print errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")
        
        # Print warnings
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        return failed == 0
    
    def get_results(self):
        """Get test results for integration with other tools."""
        return {
            'passed': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Lua syntax in LuminariGUI XML')
    parser.add_argument('--xml', default='LuminariGUI.xml', help='XML file to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode - only errors')
    
    args = parser.parse_args()
    
    tester = LuaSyntaxTester(args.xml)
    
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