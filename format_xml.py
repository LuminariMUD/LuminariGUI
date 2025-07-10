#!/usr/bin/env python3
"""
XML Formatting Script for LuminariGUI
Formats and pretty-prints the Mudlet package XML file.
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sys
import os
import shutil

def format_xml(input_file, output_file=None, backup=True):
    """Format XML file with proper indentation and structure."""
    try:
        # If no output file specified, format in place
        if output_file is None:
            output_file = input_file
            
        # Create backup if formatting in place
        if backup and input_file == output_file:
            backup_file = f"{input_file}.backup"
            shutil.copy2(input_file, backup_file)
            print(f"Created backup: {backup_file}")
            
        print(f"Formatting {input_file}...")
        
        # Parse the XML
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # Convert to string for pretty printing
        xml_str = ET.tostring(root, encoding='unicode')
        
        # Use minidom for pretty printing
        dom = minidom.parseString(xml_str)
        
        # Custom pretty print to handle CDATA and special content better
        pretty_xml = dom.toprettyxml(indent="	", encoding=None)
        
        # Remove extra blank lines that minidom adds
        lines = pretty_xml.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Skip the XML declaration that minidom adds (we'll add our own)
            if line.strip().startswith('<?xml'):
                continue
            # Skip completely empty lines
            if line.strip():
                formatted_lines.append(line.rstrip())
                
        # Write formatted XML with proper declaration
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE MudletPackage>\n')
            f.write('\n'.join(formatted_lines))
            f.write('\n')
            
        # Verify the formatted file is still valid
        print("Verifying formatted XML...")
        verify_tree = ET.parse(output_file)
        
        print(f"✅ Successfully formatted {input_file}")
        if output_file != input_file:
            print(f"   Output saved to: {output_file}")
            
        # Report file size change
        original_size = os.path.getsize(input_file)
        new_size = os.path.getsize(output_file)
        size_diff = new_size - original_size
        
        print(f"\nFile size:")
        print(f"  Original: {original_size:,} bytes")
        print(f"  Formatted: {new_size:,} bytes")
        print(f"  Difference: {size_diff:+,} bytes ({size_diff/original_size*100:+.1f}%)")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML Parse Error: {e}")
        print("   The XML file is not well-formed and cannot be formatted.")
        print("   Please run validate_xml.py first to identify issues.")
        return False
    except Exception as e:
        print(f"❌ Error formatting XML: {e}")
        return False

def main():
    """Main entry point for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Format Mudlet package XML files')
    parser.add_argument('input_file', nargs='?', default='LuminariGUI.xml',
                        help='Input XML file (default: LuminariGUI.xml)')
    parser.add_argument('-o', '--output', dest='output_file',
                        help='Output file (default: format in place)')
    parser.add_argument('--no-backup', action='store_true',
                        help='Do not create backup when formatting in place')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found.")
        sys.exit(1)
        
    # Format the XML
    success = format_xml(args.input_file, args.output_file, 
                        backup=not args.no_backup)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()