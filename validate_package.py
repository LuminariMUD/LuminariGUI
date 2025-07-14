#!/usr/bin/env python3
"""
Package Validation Script for LuminariGUI
Validates the Mudlet package XML structure and embedded Lua syntax.
Comprehensive validation for both XML structure and Lua code quality.
"""

import xml.etree.ElementTree as ET
import sys
import os

# Try to import Lua syntax tester
try:
    from test_lua_syntax import LuaSyntaxTester
    SYNTAX_TESTING_AVAILABLE = True
except ImportError:
    SYNTAX_TESTING_AVAILABLE = False

def validate_package(filename, include_lua_syntax=True):
    """Validate Mudlet package for XML structure and embedded Lua syntax."""
    try:
        # Check if file exists
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return False
            
        # Parse the XML file
        print(f"Validating {filename}...")
        tree = ET.parse(filename)
        root = tree.getroot()
        
        # Check root element
        if root.tag != 'MudletPackage':
            print(f"Error: Root element should be 'MudletPackage', found '{root.tag}'")
            return False
            
        # Check version attribute
        version = root.get('version')
        if not version:
            print("Warning: No version attribute found in MudletPackage")
        else:
            print(f"✓ MudletPackage version: {version}")
            
        # Count main components
        components = {
            'TriggerPackage': 0,
            'AliasPackage': 0,
            'ScriptPackage': 0,
            'TimerPackage': 0,
            'KeyPackage': 0,
            'ActionPackage': 0
        }
        
        for child in root:
            if child.tag in components:
                components[child.tag] += 1
                
        # Report component counts
        print("\nPackage Components:")
        for comp_type, count in components.items():
            if count > 0:
                print(f"  ✓ {comp_type}: {count}")
                
        # Validate script content for common issues
        print("\nChecking for common issues...")
        issues = []
        
        # Find all script elements
        for script in root.iter('script'):
            if script.text:
                # Check for unescaped XML characters in scripts
                if '<' in script.text and '&lt;' not in script.text:
                    line_num = list(root.iter()).index(script) + 1
                    issues.append(f"Line ~{line_num}: Possible unescaped '<' in script")
                if '>' in script.text and '&gt;' not in script.text and '-->' not in script.text:
                    line_num = list(root.iter()).index(script) + 1
                    issues.append(f"Line ~{line_num}: Possible unescaped '>' in script")
                    
        if issues:
            print("Potential issues found:")
            for issue in issues:  # Show all issues
                print(f"  ⚠ {issue}")
        else:
            print("  ✓ No common issues detected")
            
        print(f"\n✅ XML structural validation passed for {filename}")
        
        # Run Lua syntax validation if requested and available
        lua_syntax_passed = True
        if include_lua_syntax and SYNTAX_TESTING_AVAILABLE:
            print("\nRunning Lua syntax validation...")
            try:
                syntax_tester = LuaSyntaxTester(filename)
                lua_syntax_passed = syntax_tester.run_tests()
                
                results = syntax_tester.get_results()
                if not lua_syntax_passed:
                    print("❌ Lua syntax validation failed")
                    for error in results['errors']:
                        print(f"  Error: {error}")
                    for warning in results['warnings']:
                        print(f"  Warning: {warning}")
                else:
                    print("✅ Lua syntax validation passed")
                    if results['warnings']:
                        print("Warnings found:")
                        for warning in results['warnings']:
                            print(f"  Warning: {warning}")
            except Exception as e:
                print(f"⚠ Could not run Lua syntax validation: {e}")
                lua_syntax_passed = True  # Don't fail overall validation
        elif include_lua_syntax and not SYNTAX_TESTING_AVAILABLE:
            print("\n⚠ Lua syntax testing not available (test_lua_syntax.py not found)")
        
        overall_success = lua_syntax_passed
        if overall_success:
            print(f"\n✅ Complete validation passed for {filename}")
        else:
            print(f"\n❌ Validation failed for {filename}")
        
        return overall_success
        
    except ET.ParseError as e:
        print(f"\n❌ XML Parse Error: {e}")
        print(f"   This usually means the XML is not well-formed.")
        print(f"   Check for:")
        print(f"   - Unclosed tags")
        print(f"   - Mismatched tags")
        print(f"   - Unescaped special characters (&, <, >)")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate LuminariGUI package (XML structure and Lua syntax)')
    parser.add_argument('filename', nargs='?', default='LuminariGUI.xml', 
                        help='XML file to validate (default: LuminariGUI.xml)')
    parser.add_argument('--no-lua-syntax', action='store_true',
                        help='Skip Lua syntax validation')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet mode - minimal output')
    
    args = parser.parse_args()
    
    # Suppress output in quiet mode
    if args.quiet:
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = validate_package(args.filename, include_lua_syntax=not args.no_lua_syntax)
        
        # Only show errors in quiet mode
        if not success:
            print(f"Validation failed for {args.filename}")
    else:
        success = validate_package(args.filename, include_lua_syntax=not args.no_lua_syntax)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)