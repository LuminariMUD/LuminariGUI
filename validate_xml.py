#!/usr/bin/env python3
"""
XML Validation Script for LuminariGUI
Validates the Mudlet package XML structure and reports errors.
"""

import xml.etree.ElementTree as ET
import sys
import os

def validate_xml(filename):
    """Validate XML file for well-formedness and basic structure."""
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
            for issue in issues[:10]:  # Limit to first 10 issues
                print(f"  ⚠ {issue}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more issues")
        else:
            print("  ✓ No common issues detected")
            
        print(f"\n✅ XML validation passed for {filename}")
        return True
        
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
    # Default to LuminariGUI.xml if no argument provided
    filename = sys.argv[1] if len(sys.argv) > 1 else "LuminariGUI.xml"
    
    # Exit with appropriate code
    if validate_xml(filename):
        sys.exit(0)
    else:
        sys.exit(1)