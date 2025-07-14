# LuminariGUI Refactoring Plan

## Executive Summary

This document outlines a comprehensive plan to refactor the monolithic `LuminariGUI.xml` file (4,412 lines) into a modular architecture that maintains all existing functionality while dramatically improving maintainability, collaboration workflows, and development experience.

## Current Architecture Analysis

### File Structure Overview
- **Total Lines**: 4,412
- **File Type**: Mudlet XML Package
- **Major Components**: Triggers, Aliases, Scripts, Actions, Keys, Help

### Component Breakdown

#### 1. Trigger Systems (Lines 4-507)
```xml
<TriggerPackage>
  <TriggerGroup name="LuminariGUI">
    <TriggerGroup name="YATCOConfig">      <!-- Lines 20-191 (171 lines) -->
    <TriggerGroup name="GUI">              <!-- Lines 192-506 (314 lines) -->
```

**YATCOConfig Triggers (171 lines)**:
- Tell capture (lines 35-63)
- Congrats capture (lines 64-92) 
- Chat capture (lines 93-117)
- Auction capture (lines 118-142)
- Group capture (lines 143-167)
- Wiznet capture (lines 168-190)

**GUI Triggers (314 lines)**:
- Wilderness map capture (lines 207-291) - 84 lines
- Room map capture (lines 292-378) - 86 lines
- Blank line gagging (lines 379-398) - 19 lines
- Cast console triggers (lines 399-504) - 105 lines

#### 2. Alias Systems (Lines 509-634)
```xml
<AliasPackage>
  <AliasGroup name="LuminariGUI">
    <AliasGroup name="Toggles">            <!-- Lines 516-539 -->
    <AliasGroup name="YATCO">              <!-- Lines 540-632 -->
```

**Toggle Aliases (23 lines)**:
- Gag chat toggle
- Show self toggle

**YATCO Aliases (92 lines)**:
- Debug commands
- Chat system controls
- Blinking toggles

#### 3. Script Systems (Lines 636-4407)
```xml
<ScriptPackage>
  <ScriptGroup name="LuminariGUI">
    <ScriptGroup name="MSDPMapper">        <!-- Lines 643-1416 (773 lines) -->
    <ScriptGroup name="GUI">               <!-- Lines 1420-3690 (2270 lines) -->
    <ScriptGroup name="YATCOConfig">       <!-- Lines 3691-3871 (180 lines) -->
    <ScriptGroup name="YATCO">             <!-- Lines 3872-4350 (478 lines) -->
```

**MSDPMapper (773 lines)** - Largest single component:
- Terrain type definitions
- Movement algorithms
- Room creation logic
- Pathfinding system

**GUI System (2,270 lines)** - Most complex component:
- CSSMan utility (42 lines)
- Core GUI framework (2,228 lines)
  - Background creation
  - Border management 
  - Gauge systems
  - Tabbed windows
  - Button management
  - MSDP event handling
  - Resource cleanup

**YATCO Systems (658 lines)**:
- Configuration (180 lines)
- Core chat system (478 lines)

## Proposed Modular Architecture

### Directory Structure
```
src/
├── template.xml                    # Base XML package structure
├── metadata.json                   # Assembly configuration
├── triggers/
│   ├── chat_capture.xml           # YATCOConfig communication triggers
│   ├── map_processing.xml         # Map capture and processing
│   ├── cast_console.xml           # Spell casting event triggers
│   └── utility.xml                # Line gagging and utility triggers
├── aliases/
│   ├── toggles.xml                # UI toggle commands
│   └── yatco_commands.xml         # Chat system and debug aliases
├── scripts/
│   ├── core/
│   │   ├── msdp_mapper.lua        # 773-line mapper system
│   │   ├── css_manager.lua        # CSSMan styling utility
│   │   └── resource_cleanup.lua   # Error handling & resource management
│   ├── gui/
│   │   ├── initialization.lua     # GUI.init and system setup
│   │   ├── backgrounds.lua        # Container and background creation
│   │   ├── borders.lua            # Frame and border management
│   │   ├── gauges.lua            # Health/movement/XP bar systems
│   │   ├── tabbed_windows.lua    # Player/Affects/Group tab system
│   │   ├── button_system.lua     # Legend/Map mode button controls
│   │   ├── cast_console.lua      # Spell casting feedback system
│   │   ├── affects_display.lua   # Buffs/debuffs icon management
│   │   ├── group_display.lua     # Group member information
│   │   ├── player_display.lua    # Character stats and information
│   │   ├── room_legend.lua       # Room info and map legend
│   │   ├── msdp_handlers.lua     # MSDP event processing
│   │   └── scrollbar_styling.lua # Custom UI styling
│   └── yatco/
│       ├── config.lua            # YATCO configuration options
│       ├── chat_core.lua         # Main tabbed chat system
│       ├── debugging.lua         # Debug utilities and commands
│       └── shared_utilities.lua  # Common YATCO functions
└── build/
    └── LuminariGUI.xml           # Generated output file
```

### Component Size Analysis

| Component Category | Current Lines | Proposed Files | Avg File Size |
|-------------------|---------------|----------------|---------------|
| MSDPMapper | 773 | 1 | 773 |
| GUI Core | 2,270 | 12 | 189 |
| YATCO System | 658 | 4 | 164 |
| Triggers | 503 | 4 | 126 |
| Aliases | 125 | 2 | 63 |
| **Total** | **4,329** | **23** | **188** |

## Implementation Strategy

### Phase 1: Infrastructure Setup (Days 1-3)

#### 1.1 Create Build System Enhancement
```python
# Extend create_package.py with modular assembly
def assemble_modular_package():
    """
    Reads metadata.json and assembles components into final XML
    """
    # Load assembly configuration
    # Process triggers, aliases, scripts
    # Validate component integrity
    # Generate final XML package
```

#### 1.2 Create Metadata Configuration
```json
{
  "package": {
    "name": "LuminariGUI",
    "version": "1.001"
  },
  "triggers": [
    "triggers/chat_capture.xml",
    "triggers/map_processing.xml", 
    "triggers/cast_console.xml",
    "triggers/utility.xml"
  ],
  "aliases": [
    "aliases/toggles.xml",
    "aliases/yatco_commands.xml"
  ],
  "scripts": {
    "core": [
      "scripts/core/msdp_mapper.lua",
      "scripts/core/css_manager.lua",
      "scripts/core/resource_cleanup.lua"
    ],
    "gui": [
      "scripts/gui/initialization.lua",
      "scripts/gui/backgrounds.lua",
      "scripts/gui/borders.lua",
      "scripts/gui/gauges.lua",
      "scripts/gui/tabbed_windows.lua",
      "scripts/gui/button_system.lua",
      "scripts/gui/cast_console.lua",
      "scripts/gui/affects_display.lua",
      "scripts/gui/group_display.lua",
      "scripts/gui/player_display.lua",
      "scripts/gui/room_legend.lua",
      "scripts/gui/msdp_handlers.lua",
      "scripts/gui/scrollbar_styling.lua"
    ],
    "yatco": [
      "scripts/yatco/config.lua",
      "scripts/yatco/chat_core.lua", 
      "scripts/yatco/debugging.lua",
      "scripts/yatco/shared_utilities.lua"
    ]
  }
}
```

#### 1.3 Create Template Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE MudletPackage>
<MudletPackage version="1.001">
    <!-- Triggers will be inserted here -->
    <TriggerPackage>
        <!-- TRIGGER_CONTENT -->
    </TriggerPackage>
    
    <!-- Timers (currently empty) -->
    <TimerPackage/>
    
    <!-- Aliases will be inserted here -->
    <AliasPackage>
        <!-- ALIAS_CONTENT -->  
    </AliasPackage>
    
    <!-- Actions (currently empty) -->
    <ActionPackage/>
    
    <!-- Scripts will be inserted here -->
    <ScriptPackage>
        <!-- SCRIPT_CONTENT -->
    </ScriptPackage>
    
    <!-- Keys (currently empty) -->
    <KeyPackage/>
    
    <!-- Help -->
    <HelpPackage>
        <helpURL/>
    </HelpPackage>
</MudletPackage>
```

### Phase 2: Extract Core Systems (Days 4-8)

#### 2.1 Extract MSDPMapper (Day 4)
**Priority: High** - Largest single component (773 lines)

Extract from lines 647-1416:
- Terrain type definitions
- Movement vector calculations  
- Room creation algorithms
- Speedwalk system
- Event handlers

**File**: `scripts/core/msdp_mapper.lua`

#### 2.2 Extract CSSMan Utility (Day 4)  
**Priority: Low** - Small, self-contained (42 lines)

Extract from lines 1430-1468:
- CSS parsing and management
- Style manipulation functions

**File**: `scripts/core/css_manager.lua`

#### 2.3 Extract Resource Cleanup System (Day 5)
**Priority: High** - Critical for stability (238 lines)

Extract from lines 3607-3678:
- Event handler tracking
- Timer management
- Error boundaries
- Cleanup functions

**File**: `scripts/core/resource_cleanup.lua`

### Phase 3: Modularize GUI System (Days 9-15)

#### 3.1 Extract GUI Initialization (Day 9)
Extract GUI.init() and core setup logic:
- Background creation
- Border setting  
- Box initialization
- Event handler migration

**File**: `scripts/gui/initialization.lua`

#### 3.2 Extract Background & Container System (Day 10)
Extract from lines 1538-1558:
- GUI.Left, GUI.Right, GUI.Bottom creation
- Background styling
- Container positioning

**File**: `scripts/gui/backgrounds.lua`

#### 3.3 Extract Border & Frame System (Day 10)
Extract createFrame() function and border management:
- 9-slice frame generation
- Border positioning algorithms
- Frame styling

**File**: `scripts/gui/borders.lua`

#### 3.4 Extract Gauge System (Day 11)
Extract from lines 1661-1847:
- Health gauge management
- Movement gauge system
- Experience tracking
- Enemy health display
- Action icons

**File**: `scripts/gui/gauges.lua`

#### 3.5 Extract Tabbed Window System (Day 12)
Extract tabbed info window system:
- Tab creation and management
- Content switching logic
- Styling and layout

**File**: `scripts/gui/tabbed_windows.lua`

#### 3.6 Extract Specialized Display Systems (Days 13-14)

**Cast Console System**:
- Spell casting feedback
- Timer management
- Status display

**File**: `scripts/gui/cast_console.lua`

**Affects Display System** (324 lines):
- Icon management
- Mode detection
- Spell-like affects
- Visual representation

**File**: `scripts/gui/affects_display.lua`

**Group Display System**:
- Member information processing
- Health/movement display
- Leader status handling

**File**: `scripts/gui/group_display.lua`

**Player Display System**: 
- Character stats
- Attribute display
- Position information

**File**: `scripts/gui/player_display.lua`

**Room/Legend System**:
- Room information display
- Map legend generation
- Terrain symbol mapping

**File**: `scripts/gui/room_legend.lua`

#### 3.7 Extract MSDP & Event Handlers (Day 15)
- MSDP protocol handling
- Event registration
- Data processing functions

**File**: `scripts/gui/msdp_handlers.lua`

### Phase 4: Extract Communication Systems (Days 16-18)

#### 4.1 Extract Trigger Systems (Day 16)

**Chat Capture Triggers**:
Extract YATCOConfig triggers (lines 35-190):
- Tell capture
- Chat capture  
- Group communication
- Channel monitoring

**File**: `triggers/chat_capture.xml`

**Map Processing Triggers**:
Extract GUI map triggers (lines 207-378):
- Wilderness map capture
- Room map capture
- Map line processing

**File**: `triggers/map_processing.xml`

**Cast Console Triggers**:
Extract casting triggers (lines 414-503):
- Cast start detection
- Completion handling
- Abort/cancel processing

**File**: `triggers/cast_console.xml`

**Utility Triggers**:
Extract utility functions:
- Blank line gagging
- General line processing

**File**: `triggers/utility.xml`

#### 4.2 Extract Alias Systems (Day 17)

**Toggle Aliases**:
Extract toggle commands (lines 522-538):
- Chat gagging toggle
- Self display toggle

**File**: `aliases/toggles.xml`

**YATCO Command Aliases**:
Extract YATCO aliases (lines 546-630):
- Debug commands
- Chat controls
- Utility functions

**File**: `aliases/yatco_commands.xml`

#### 4.3 Extract YATCO System (Day 18)

**YATCO Configuration**:
Extract configuration options (lines 3704-3870):
- Chat settings
- Display preferences
- Channel definitions

**File**: `scripts/yatco/config.lua`

**YATCO Core System**:
Extract main chat functionality (lines 3975-4221):
- Tab management
- Window creation
- Message handling

**File**: `scripts/yatco/chat_core.lua`

**YATCO Debugging**:
Extract debug utilities (lines 3901-3957):
- Debug category management
- Error reporting
- Development tools

**File**: `scripts/yatco/debugging.lua`

### Phase 5: Integration & Testing (Days 19-21)

#### 5.1 Build System Integration (Day 19)
- Implement assembly logic in `create_package.py`
- Add validation for component integrity
- Test build process with modular components

#### 5.2 Functionality Testing (Day 20)  
- Verify all GUI components work correctly
- Test MSDP mapper functionality
- Validate chat system integration
- Check trigger/alias functionality

#### 5.3 Performance & Compatibility Testing (Day 21)
- Compare performance with original monolithic version
- Test memory usage and resource cleanup
- Verify Mudlet compatibility
- Validate all event handlers function correctly

## Technical Implementation Details

### Build System Enhancement

```python
import json
import xml.etree.ElementTree as ET
from pathlib import Path

class ModularPackageBuilder:
    def __init__(self, config_path="metadata.json"):
        with open(config_path) as f:
            self.config = json.load(f)
    
    def assemble_triggers(self):
        """Combine all trigger XML files"""
        trigger_root = ET.Element("TriggerGroup", 
                                 isActive="yes", isFolder="yes", 
                                 isTempTrigger="no", isMultiline="no")
        
        for trigger_file in self.config["triggers"]:
            trigger_xml = ET.parse(trigger_file)
            trigger_root.extend(trigger_xml.getroot())
        
        return trigger_root
    
    def assemble_scripts(self):
        """Combine all Lua scripts into XML structure"""
        script_root = ET.Element("ScriptGroup", 
                                isActive="yes", isFolder="yes")
        
        # Process each script category
        for category, scripts in self.config["scripts"].items():
            category_group = ET.SubElement(script_root, "ScriptGroup",
                                         isActive="yes", isFolder="yes")
            category_group.find("name").text = category.title()
            
            for script_file in scripts:
                script_elem = self.create_script_element(script_file)
                category_group.append(script_elem)
        
        return script_root
    
    def create_script_element(self, script_path):
        """Convert Lua file to XML script element"""
        script_elem = ET.Element("Script", isActive="yes", isFolder="no")
        
        # Extract script name from file path
        name_elem = ET.SubElement(script_elem, "name")
        name_elem.text = Path(script_path).stem.replace('_', ' ').title()
        
        # Read and embed Lua content
        with open(script_path) as f:
            script_content = f.read()
        
        script_text_elem = ET.SubElement(script_elem, "script")
        script_text_elem.text = script_content
        
        return script_elem
    
    def build_package(self, output_path="build/LuminariGUI.xml"):
        """Build complete XML package"""
        # Load template
        template = ET.parse("src/template.xml")
        root = template.getroot()
        
        # Insert assembled components
        trigger_package = root.find("TriggerPackage")
        trigger_package.extend(self.assemble_triggers())
        
        script_package = root.find("ScriptPackage") 
        script_package.extend(self.assemble_scripts())
        
        # Write final package
        template.write(output_path, encoding="UTF-8", xml_declaration=True)
```

### Component Validation System

```python
class ComponentValidator:
    def validate_lua_syntax(self, lua_file):
        """Validate Lua syntax before assembly"""
        # Use lua parser or subprocess to check syntax
        pass
    
    def validate_xml_structure(self, xml_file):
        """Validate XML component structure"""
        try:
            ET.parse(xml_file)
            return True
        except ET.ParseError as e:
            print(f"XML validation failed for {xml_file}: {e}")
            return False
    
    def validate_dependencies(self):
        """Check for missing function/variable dependencies"""
        # Static analysis to ensure all references are satisfied
        pass
```

### Development Workflow Integration

```bash
# Development workflow scripts
scripts/
├── dev_build.sh          # Quick build for development
├── validate_components.sh # Run all validations
└── watch_changes.sh      # Auto-rebuild on file changes
```

## Risk Mitigation Strategies

### 1. Functionality Preservation
- **Validation**: Comprehensive testing after each extraction
- **Backup**: Maintain original XML file as reference
- **Incremental**: Extract one component at a time
- **Testing**: Automated testing of core functionality

### 2. Dependency Management
- **Mapping**: Document all inter-component dependencies
- **Validation**: Build-time dependency checking
- **Isolation**: Minimize cross-component coupling
- **Interfaces**: Define clear component boundaries

### 3. Performance Considerations
- **Benchmarking**: Compare performance before/after
- **Optimization**: Profile critical paths
- **Memory**: Monitor resource usage patterns
- **Loading**: Ensure initialization order is preserved

### 4. Team Coordination
- **Documentation**: Comprehensive component documentation
- **Standards**: Consistent coding and naming conventions
- **Reviews**: Code review process for extractions
- **Communication**: Clear progress tracking and updates

## Expected Benefits

### 1. Development Experience
- **IDE Support**: Full syntax highlighting and completion for Lua files
- **Debugging**: Easier debugging with proper file structure
- **Navigation**: Quick file jumping and symbol search
- **Refactoring**: Safe refactoring with modern IDE tools

### 2. Collaboration Workflow
- **Parallel Development**: Multiple developers can work simultaneously
- **Conflict Resolution**: Cleaner merge conflicts with smaller files
- **Code Review**: Focused reviews on specific components
- **Responsibility**: Clear ownership of individual systems

### 3. Maintenance Efficiency  
- **Bug Isolation**: Issues confined to specific components
- **Feature Addition**: New features in dedicated files
- **Testing**: Component-level unit testing
- **Documentation**: Inline documentation for each component

### 4. Long-term Architecture
- **Scalability**: Easy addition of new GUI components
- **Modularity**: Clean separation of concerns
- **Reusability**: Components usable in other projects
- **Flexibility**: Individual component updates without full rebuild

## Success Metrics

### Quantitative Measures
- **File Count**: 23 focused files vs 1 monolithic file
- **Average File Size**: 188 lines vs 4,412 lines
- **Build Time**: Target <5 seconds for full assembly
- **Component Coverage**: 100% of original functionality preserved

### Qualitative Measures
- **Developer Satisfaction**: Survey team on development experience
- **Bug Resolution Time**: Measure time to fix issues
- **Feature Development Speed**: Track new feature implementation time
- **Code Review Quality**: Assess review thoroughness and speed

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Infrastructure | 3 days | Build system, templates, metadata |
| Phase 2: Core Systems | 5 days | MSDPMapper, CSSMan, Resource Cleanup |
| Phase 3: GUI Modularization | 7 days | All GUI components extracted |
| Phase 4: Communication Systems | 3 days | Triggers, aliases, YATCO |
| Phase 5: Integration & Testing | 3 days | Full system validation |
| **Total** | **21 days** | **Complete modular architecture** |

## Conclusion

This refactoring plan transforms a 4,412-line monolithic XML file into a well-organized, maintainable modular architecture with 23 focused components. The approach prioritizes functionality preservation while delivering significant improvements to the development experience, collaboration workflow, and long-term maintainability.

The phased implementation strategy minimizes risk while ensuring continuous progress, and the enhanced build system maintains the convenience of single-file distribution while enabling modern development practices.