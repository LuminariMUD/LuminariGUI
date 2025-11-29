#!/usr/bin/env python3
"""
Handler Analysis Script for LuminariGUI
Analyzes Lua scripts within the XML package to track event handler and timer usage.
Reports on creation vs cleanup of handlers/timers to help identify potential memory leaks.
"""

import xml.etree.ElementTree as ET
import re
import os

# Get script directory for relative path calculations
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def get_project_path(relative_path):
    """Get absolute path relative to project root"""
    return os.path.join(PROJECT_ROOT, relative_path)

tree = ET.parse(get_project_path('LuminariGUI.xml'))
root = tree.getroot()

# Find all Script elements with their names
def find_script_name(elem):
    # Look for name element in Script
    if elem.tag == 'Script':
        name_elem = elem.find('name')
        if name_elem is not None and name_elem.text:
            return name_elem.text
    return None

# Analyze each script
results = {}

for script_elem in root.iter('Script'):
    script_name = find_script_name(script_elem)
    if not script_name:
        continue
    
    script_text_elem = script_elem.find('script')
    if script_text_elem is None or not script_text_elem.text:
        continue
    
    script_text = script_text_elem.text
    
    # Count handlers and timers
    handler_creates = len(re.findall(r'registerAnonymousEventHandler\s*\(', script_text))
    handler_kills = len(re.findall(r'killAnonymousEventHandler\s*\(', script_text))
    timer_creates = len(re.findall(r'tempTimer\s*\(', script_text))
    timer_kills = len(re.findall(r'killTimer\s*\(', script_text))
    
    if handler_creates > 0 or timer_creates > 0:
        results[script_name] = {
            'handlers': {'created': handler_creates, 'killed': handler_kills},
            'timers': {'created': timer_creates, 'killed': timer_kills}
        }

print(f"{'Script Name':<30} | {'Handlers (New/Kill)':<20} | {'Timers (New/Kill)':<20}")
print("-" * 80)

for name, data in sorted(results.items()):
    handlers = f"{data['handlers']['created']}/{data['handlers']['killed']}"
    timers = f"{data['timers']['created']}/{data['timers']['killed']}"
    print(f"{name:<30} | {handlers:<20} | {timers:<20}")
