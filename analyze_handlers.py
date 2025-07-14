import xml.etree.ElementTree as ET
import re

tree = ET.parse('LuminariGUI.xml')
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

# Print results
print("Resource usage by script:")
print("-" * 50)
for script, data in sorted(results.items()):
    h_created = data['handlers']['created']
    h_killed = data['handlers']['killed']
    t_created = data['timers']['created']
    t_killed = data['timers']['killed']
    
    if h_created > h_killed or t_created > t_killed:
        print(f"\n{script}:")
        if h_created > 0:
            print(f"  Event handlers: {h_created} created, {h_killed} killed")
        if t_created > 0:
            print(f"  Timers: {t_created} created, {t_killed} killed")
