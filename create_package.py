#!/usr/bin/env python3
"""
LuminariGUI Package Creator
Creates a .mpackage file from the XML source and resources

Based on PACKAGING.md documentation, this script:
1. Creates a temporary directory structure
2. Copies the XML file (main package content)
3. Copies the images/ directory (status effect icons, UI assets)
4. Generates config.lua with proper metadata
5. Creates ZIP archive with .mpackage extension
6. Verifies package contents

Usage:
    python3 create_package.py
    python3 create_package.py --xml LuminariGUI.xml --output LuminariGUI-v2.1.0.mpackage
    python3 create_package.py --version 2.1.0
"""

import os
import sys
import shutil
import tempfile
import zipfile
from datetime import datetime
import argparse
import re

def get_version_from_changelog():
    """Extract version from CHANGELOG.md"""
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for version patterns like [2.0.0] - must be numeric versions
        versions = re.findall(r'\[([0-9]+\.[0-9]+\.[0-9]+)\]', content)
        
        # Return first semantic version found
        if versions:
            return versions[0]
        
        return "2.0.0"  # Default fallback
    except Exception as e:
        print(f"⚠️  Warning: Could not read CHANGELOG.md: {e}")
        return "2.0.0"

def create_config_lua(version):
    """Create config.lua with proper metadata"""
    return f'''mpackage = "LuminariGUI"
author = "LuminariMUD Team"
title = "LuminariGUI"
description = [[
Enhanced MUD client interface for LuminariMUD with advanced features
including chat management, mapping, status effects, and more.
]]
version = "{version}"
created = "{datetime.now().strftime('%Y-%m-%d')}"
modified = "{datetime.now().strftime('%Y-%m-%d')}"
dependencies = {{}}
'''

def validate_xml_exists(xml_file):
    """Check if XML file exists and is readable"""
    if not os.path.exists(xml_file):
        print(f"❌ Error: {xml_file} not found")
        return False
    
    if not os.path.isfile(xml_file):
        print(f"❌ Error: {xml_file} is not a file")
        return False
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            # Read first few lines to check if it's XML
            first_line = f.readline().strip()
            if not first_line.startswith('<?xml'):
                print(f"⚠️  Warning: {xml_file} doesn't appear to be an XML file")
    except Exception as e:
        print(f"❌ Error reading {xml_file}: {e}")
        return False
    
    return True

def create_mpackage(xml_file="LuminariGUI.xml", output_file="LuminariGUI.mpackage", version=None):
    """Create .mpackage file from XML source"""
    
    # Validate source file
    if not validate_xml_exists(xml_file):
        return False
    
    # Get version from changelog if not provided
    if version is None:
        version = get_version_from_changelog()
    
    print(f"📦 Creating package version: {version}")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🔧 Working in temporary directory: {temp_dir}")
        
        # Copy XML file
        try:
            shutil.copy2(xml_file, temp_dir)
            print(f"✅ Copied {xml_file}")
        except Exception as e:
            print(f"❌ Error copying {xml_file}: {e}")
            return False
        
        # Copy images directory if it exists
        images_dir = "images"
        if os.path.exists(images_dir) and os.path.isdir(images_dir):
            try:
                shutil.copytree(images_dir, os.path.join(temp_dir, "images"))
                print(f"✅ Copied {images_dir}/ directory")
            except Exception as e:
                print(f"⚠️  Warning: Could not copy images directory: {e}")
        else:
            print(f"⚠️  Warning: {images_dir}/ directory not found, skipping")
        
        # Create config.lua
        config_content = create_config_lua(version)
        config_path = os.path.join(temp_dir, "config.lua")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"✅ Created config.lua")
        except Exception as e:
            print(f"❌ Error creating config.lua: {e}")
            return False
        
        # Create ZIP archive (which IS the .mpackage file)
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_path)
                        print(f"📁 Added: {arc_path}")
        except Exception as e:
            print(f"❌ Error creating ZIP archive: {e}")
            return False
    
    # Verify the package was created
    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / 1024 / 1024
        print(f"✅ Package created successfully: {output_file} ({size_mb:.1f} MB)")
        
        # Show package contents
        print("\n📋 Package contents:")
        try:
            with zipfile.ZipFile(output_file, 'r') as zipf:
                total_files = 0
                total_size = 0
                for info in zipf.infolist():
                    print(f"   {info.filename} ({info.file_size:,} bytes)")
                    total_files += 1
                    total_size += info.file_size
                print(f"\n📊 Total: {total_files} files, {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        except Exception as e:
            print(f"⚠️  Warning: Could not list package contents: {e}")
        
        return True
    else:
        print(f"❌ Failed to create package: {output_file}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Create .mpackage file from XML source',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 create_package.py
  python3 create_package.py --xml LuminariGUI.xml --output LuminariGUI-v2.1.0.mpackage
  python3 create_package.py --version 2.1.0
  
Note: .mpackage files are ZIP archives containing XML data and metadata.
'''
    )
    
    parser.add_argument('--xml', default='LuminariGUI.xml', 
                       help='Source XML file (default: LuminariGUI.xml)')
    parser.add_argument('--output', default='LuminariGUI.mpackage', 
                       help='Output .mpackage file (default: LuminariGUI.mpackage)')
    parser.add_argument('--version', 
                       help='Override version (default: auto-detect from CHANGELOG.md)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    print("🚀 LuminariGUI Package Creator")
    print("=" * 40)
    
    if args.verbose:
        print(f"📂 Source XML: {args.xml}")
        print(f"📦 Output package: {args.output}")
        print(f"🔢 Version: {args.version or 'auto-detect'}")
        print()
    
    success = create_mpackage(args.xml, args.output, args.version)
    
    if success:
        print("\n✅ Package creation completed successfully!")
        print(f"📦 Ready for distribution: {args.output}")
        print("\n💡 Usage instructions:")
        print("   1. Import via Mudlet Package Manager")
        print("   2. Or extract and import XML manually")
        print("   3. .mpackage files are ZIP archives - can be extracted with any ZIP tool")
    else:
        print("\n❌ Package creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 