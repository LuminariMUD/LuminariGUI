# Ideas for Design Taken from @NyyLIB013dev.xml

## Overview
NyyLIB013dev.xml is a comprehensive MUD GUI package that demonstrates advanced UI patterns and implementation techniques for Mudlet. This document extracts key design ideas and patterns that can be applied to LuminariGUI.

## 1. UI Framework Architecture

### 1.1 Geyser Framework Usage
The package extensively uses Mudlet's Geyser UI framework for creating GUI components:

```lua
-- Main window containers
gGroupStatusWindow = Geyser.Label:new({name="gGroupStatusWindow", x="0%", y="-1c", width="100%", height="1c"})
window = Geyser.Label:new({name="gIconBarWindow", x="0%", y=-51, width="100%", height="40"})

-- Nested containers
Geyser.Container:new({name="LeftPanel", x="1%", y="2%", width="98%", height="75%"}, label)
```

### 1.2 Adjustable Container System
Implements a sophisticated system for user-adjustable windows:

```lua
-- Creating adjustable containers that can be moved/resized by users
mapAdjCon = mapAdjCon or Adjustable.Container:new({name="mapAdjCon"})
mapAdjCon:setTitle("NyyMap")

-- Containers can convert to floating UserWindows on double-click
if minimapAdjCon.isUserWindow then
  minimapAdjCon:onDoubleClick()
  convertAdj.sendToPosition(nil, nil, "48.16%", 0, "main")
end
```

### 1.3 Layout Management
- Uses percentage-based positioning for responsive design
- Implements both HBox and VBox containers for organized layouts
- Supports docking and undocking of windows

## 2. Window Management System

### 2.1 Group Status Window
Displays party member information in a bottom status bar:

```lua
function RedrawGroupStatus()
  local bottomwin = ""
  for k,char in pairs(groupList:pc()) do
    local cls = whoclass(char) or "UNK"
    local charline = genline(char, cls, groupList:getHP(char), groupList:getMaxHP(char))
    bottomwin = bottomwin .. charline
  end
  bottomWindow:echo(parseLine(bottomwin))
end
```

### 2.2 Map Windows
Implements both full map and minimap with synchronized display:

```lua
-- Minimap implementation
function miniMap:create()
  minimapAdjCon = minimapAdjCon or Adjustable.Container:new({name="minimapAdjCon", width="28c", height="13c"})
  self.windowid = Geyser.MiniConsole:new({name="miniMap", x="5%", y="5%", width="33c", height="13c"}, miniMap.label)
end

-- Full map
NyyLIB.mapwindow = Geyser.Mapper:new({name="NyyMapper", x=0, y=10, width="100%", height="100%-10px"}, mapAdjCon)
```

### 2.3 Chat System (YATCO)
Uses demonnic's YATCO for tabbed chat management:

```lua
-- Chat configuration
demonnic.chat.use = true
demonnic.chat.channels = {"GSAY", "OOC", "NHC", "ACC", "GCC", "TELLS", "SAYS", "AUC"}

-- Appending to chat tabs
demonnic.chat:append("GSAY", whoMatch, bodyMatch)
```

## 3. Timer & Cooldown System

### 3.1 Centralized Timer Module
Implements a unified timer system for all cooldowns:

```lua
timer = timer or {}
timer.values = timer.values or {}

function timer:init()
  permTimer("MudTimer2", "", 1, [[timer:script()]])
end

function timer:set(xname, xduration)
  self.values[xname] = xduration
end

function timer:script()
  for k, v in pairs(timer.values) do
    timer.values[k] = timer.values[k] - 1
    if timer.values[k] < 0 then
      timer.values[k] = nil
      -- Call expiry function if exists
      if _G[k] then _G[k](k, 0) end
    end
  end
end
```

### 3.2 Visual Cooldown Display
- Shows countdown numbers on buttons
- Updates button images based on state
- Implements buff duration tracking

## 4. Button System

### 4.1 Dynamic Button Creation
Buttons are created based on player class and abilities:

```lua
function addbutton(createname, xbar, xid, row, xwidth, ys)
  local baseButton = Geyser.Label:new({
    name=createname .. "base", 
    x=xp, y=yp, 
    width=xwidth, height=ys
  }, window)
  
  -- Add click callback
  newbutton:setClickCallback(createname)
  
  -- Set tooltip
  newbutton:setToolTip(createname, "10")
end
```

### 4.2 Icon Management
Uses PNG images for button states:

```lua
setLabelImage("HealSong", "barHeal-on.png")
setLabelImage("StopMusic", "barStopMusic-timer.png")
setLabelImage("mysizeDisplay", "size" .. charData:get("bodysize") .. ".png")
```

### 4.3 Button Panel Organization
```lua
-- Settings button and panel
NyyLIB.buttonpanel = Geyser.HBox:new({name="buttonpanel", x=0, y=0, width="100%", height="100%"})

-- Individual buttons within panel
NyyLIB.mapbutton = Geyser.Label:new({name="mapbutton"}, NyyLIB.buttonpanel)
```

## 5. Styling & Theming

### 5.1 Qt StyleSheet Usage
```lua
function setStyle()
  local background_color = "#26192f"
  local border_color = "#b8731b"
  
  setAppStyleSheet([[
    QMainWindow {
      background: ]]..background_color..[[;
    }
    QToolButton {
      background-color: ]]..background_color..[[;
      border: 1px solid ]]..border_color..[[;
    }
  ]])
end
```

### 5.2 Border Images
```lua
-- 9-piece border system for frames
miniMap.label:setStyleSheet([[border-image: url(]] .. iconpath("frame-1.png") .. [[)]])

-- Button styling
button:setStyleSheet([[ QLabel{ border-image: url(]] .. iconpath("settings.png") .. [[);} ]])
```

### 5.3 Dynamic Font Sizing
```lua
function maxfont(charcount, windowwidth, linecount, windowheight)
  -- Calculate optimal font size based on window dimensions
  local fontsize = math.floor(windowwidth / charcount)
  if windowheight and linecount then
    local heightsize = math.floor(windowheight / linecount)
    fontsize = math.min(fontsize, heightsize)
  end
  return fontsize
end
```

## 6. Event Handling Architecture

### 6.1 Event Registration
- Uses Mudlet's event system for communication between modules
- Registers handlers for game events (combat, movement, etc.)

### 6.2 Trigger Organization
- Hierarchical trigger groups for different game systems
- Pattern matching for game text parsing
- State management through trigger enable/disable

## 7. Data Management Patterns

### 7.1 Character Data Storage
```lua
-- Centralized character data management
charData:set("level", 50)
charData:get("winMinimap", true)  -- with default value
```

### 7.2 Group Management
```lua
groupList:add(name, class, hp, maxhp)
groupList:ingroup(character)
groupList:getHP(character)
```

### 7.3 Pet/Follower Tracking
```lua
pet:getTable()
pet:getHP(petname)
pet:getInRoom(petname)
```

## 8. Window State Persistence

### 8.1 Window Position/Size Saving
- Adjustable containers save their state
- User preferences stored in charData
- Window layout can be reset with @resetgui command

### 8.2 Configuration Management
```lua
-- Window visibility states
charData:set("winMinimap", false)
charData:set("mapAdjCon", true)  -- Is it a UserWindow?
```

## 9. Performance Optimizations

### 9.1 Conditional Redraws
- Only redraw when data changes
- Use timers to batch updates
- Cache frequently accessed data

### 9.2 Buffer Management
```lua
-- Use buffers for complex displays
copyBuffer("minimapBuffer", "miniMap")
clearWindow("minimapBuffer")
```

## 10. Additional UI/UX Design Elements from NyyLIB

### 10.1 Advanced Container Features
- **Double-click to Float**: Containers convert to independent UserWindows
- **Auto-centering**: Windows center themselves within parent containers
- **Dynamic Resizing**: Containers adjust based on content
- **State Memory**: Window positions/sizes persist across sessions

### 10.2 Visual Design Elements
- **9-Piece Border System**: `border-image: url(frame-1.png)` for frames
- **Gradient Backgrounds**: HP bars with multi-stop gradients
- **Icon Overlays**: Status icons with countdown numbers
- **Transparency Effects**: `rgba(0,0,0,0%)` for disabled states
- **Border Highlighting**: Red borders for active windows

### 10.3 Button Design Patterns
- **Multi-State Images**: -on.png, -off.png, -timer.png variants
- **Countdown Overlays**: Large centered numbers on buttons
- **Color-Coded Timers**: Different colors for cooldowns vs buffs
- **Dynamic Sizing**: Buttons scale with available space
- **Tooltip Integration**: Built-in tooltip support

### 10.4 Layout Design Concepts
- **Bottom Status Bar**: Group information in horizontal strip
- **Floating Panels**: Settings, map, chat as moveable windows
- **Nested Containers**: HBox/VBox for organized layouts
- **Percentage-Based Positioning**: Responsive to window size
- **Z-Order Management**: raiseWindow() for proper layering

### 10.5 Typography & Text Design
- **Dynamic Font Sizing**: `maxfont()` calculates optimal size
- **HTML Text Rendering**: Rich text in labels and buttons
- **Color Preservation**: Hex color encoding for chat
- **Monospace Optimization**: Font sizing for fixed-width display
- **Auto-wrapping**: Text wrap based on container width

### 10.6 Interactive Design Elements
- **Click Callbacks**: Labels respond to mouse clicks
- **Hover Effects**: Visual feedback on mouse over
- **Drag Handles**: Adjustable containers can be moved
- **Resize Grips**: Visual indicators for resizable areas
- **Context Menus**: Right-click functionality

### 10.7 Animation & Feedback
- **Countdown Animations**: Numbers decrease on buttons
- **Flash Notifications**: Alert animations for events
- **Smooth Transitions**: Window show/hide effects
- **Progress Indicators**: Visual spell casting progress
- **Blink Effects**: Tab blinking for new messages

### 10.8 Color Design System
- **Semantic Colors**: Red for damage, green for healing
- **State Colors**: Different colors for different states
- **Gradient Definitions**: Health/mana bar gradients
- **Transparency Levels**: Disabled/inactive elements
- **Theme Consistency**: Unified color palette

### 10.9 Icon Design Implementation
- **Status Effect Icons**: 60+ PNG files for buffs/debuffs
- **Button State Icons**: Visual indicators for abilities
- **Directional Indicators**: Arrow icons for movement
- **Category Icons**: Different icons for spell types
- **Size Variants**: Multiple sizes for different contexts

### 10.10 Responsive Design Patterns
- **Breakpoint Handling**: Adjust layout at size thresholds
- **Flexible Grids**: Content reflows based on space
- **Collapsible Sections**: Hide/show based on window size
- **Priority Display**: Show most important info first
- **Scalable Elements**: Everything scales proportionally

## 11. Innovative UI Patterns

### 11.1 Minimap Design
- **Frame Border**: Decorative border image
- **Buffer System**: Efficient update mechanism
- **Auto Font Sizing**: Text scales to fit
- **Toggle Visualization**: Red border when active
- **Centered Display**: Auto-centers in container

### 11.2 Chat Window Design
- **Tabbed Interface**: YATCO integration
- **Channel Colors**: Each channel has unique color
- **Compact Mode**: Minimize to save space
- **History Buffer**: Scrollable message history
- **Quick Actions**: Buttons for common commands

### 11.3 Group Window Design
- **Horizontal Layout**: Efficient space usage
- **Color-Coded Health**: Visual health indicators
- **Class Icons**: Quick class identification
- **Compact Display**: Maximum info, minimum space
- **Auto-sizing**: Adjusts to group size

### 11.4 Settings Panel Design
- **Floating Window**: Independent settings panel
- **Categorized Options**: Organized by function
- **Visual Toggles**: Clear on/off states
- **Instant Apply**: Changes take effect immediately
- **Reset Options**: Return to defaults

### 11.5 Map Window Design
- **Dual Display**: Full map and minimap
- **Synchronized Views**: Both update together
- **Room Highlighting**: Current location emphasis
- **Path Visualization**: Show calculated paths
- **Zoom Controls**: Scale map display

## 12. Design Best Practices Observed

1. **Consistency**: Unified visual language across all elements
2. **Feedback**: Every action has visual/audio response
3. **Efficiency**: Minimize clicks and maximize information density
4. **Customization**: Users can adapt UI to preferences
5. **Accessibility**: Clear visual hierarchy and readable text
6. **Performance**: Smooth updates without lag
7. **Context**: UI adapts to current game state
8. **Discoverability**: Features are easy to find and understand
9. **Persistence**: UI remembers user preferences
10. **Polish**: Attention to detail in animations and transitions

## 13. Key Design Takeaways for LuminariGUI

1. **Implement Adjustable Containers** for all major UI elements
2. **Use 9-piece borders** for professional window appearance
3. **Add countdown overlays** to ability buttons
4. **Create toggle visualizations** with border highlights
5. **Implement buffer systems** for efficient updates
6. **Use gradient backgrounds** for gauges and bars
7. **Add state-based button images** (-on, -off, -timer)
8. **Implement dynamic font sizing** for responsive text
9. **Create floating panels** for settings and tools
10. **Use semantic colors** consistently throughout UI

