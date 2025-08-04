# EMCO Installation Plan for LuminariGUI

## Overview
This document outlines a comprehensive plan to replace YATCO with EMCO in LuminariGUI. The approach prioritizes safety and maintains functionality throughout the transition.

## ⚠️ CRITICAL UPDATE: Technical Corrections Applied
Based on thorough analysis of both YATCO and EMCO APIs, this plan has been updated to address:
- API incompatibility between YATCO and EMCO
- Proper compatibility layer implementation
- Complete reference mapping
- Enhanced safety measures

## Pre-Installation Checklist

### 1. Create Safety Backup
```bash
# Create a tagged commit for YATCO version
git add -A
git commit -m "BACKUP: Final YATCO version before EMCO migration"
git tag -a "yatco-final-v2.0.4.016" -m "Last stable YATCO implementation"
git push origin --tags
```

### 2. Document Current State
- [ ] Review YATCO_AUDIT.md for complete reference list (200+ references found)
- [ ] All chat triggers use `demonnic.chat:append()` pattern (7 triggers)
- [ ] Custom aliases: gag chat, dblink, dsound, set chat sound, fix chat
- [ ] Tab configuration: All, Tell, Chat, Say, Group, Auction, Congrats, Wiz
- [ ] Custom channel color prefixes implemented
- [ ] Sound notification system integrated
- [ ] DO NOT comment out code - use compatibility layer instead

### 3. Prepare EMCO Resources
- [ ] We have EMCO-main local to pull from
- [ ] Review EMCO_API_ANALYSIS.md for API differences
- [ ] Required files: emco.lua, demontools.lua, loggingconsole.lua
- [ ] Compatibility layer: EMCO_COMPATIBILITY_LAYER.lua ready

## Installation Steps

### Phase 1: Add EMCO Library (Safe - No Breaking Changes)

#### Step 1.1: Create EMCO Script Group
```xml
<ScriptGroup isActive="yes" isFolder="yes">
  <name>EMCO</name>
  <packageName>LuminariGUI</packageName>
  <script></script>
  <eventHandlerList />
</ScriptGroup>
```

#### Step 1.2: Add Core EMCO Files
Add these scripts in order within the EMCO ScriptGroup:

1. **demontools.lua** (required dependency)
```xml
<Script isActive="yes" isFolder="no">
  <name>EMCO_demontools</name>
  <script>-- Content from EMCO-main/src/resources/demontools.lua</script>
</Script>
```

2. **loggingconsole.lua** (optional but recommended)
```xml
<Script isActive="yes" isFolder="no">
  <name>EMCO_loggingconsole</name>
  <script>-- Content from EMCO-main/src/resources/loggingconsole.lua</script>
</Script>
```

3. **emco.lua** (main EMCO library)
```xml
<Script isActive="yes" isFolder="no">
  <name>EMCO_core</name>
  <script>-- Content from EMCO-main/src/resources/emco.lua</script>
</Script>
```

### Phase 2: Add Compatibility Layer

#### Step 2.1: Add EMCO Compatibility Layer Script
Add this before the initialization script:
```xml
<Script isActive="yes" isFolder="no">
  <name>EMCO_Compatibility_Layer</name>
  <script>-- Content from EMCO_COMPATIBILITY_LAYER.lua</script>
</Script>
```

### Phase 3: Create LuminariGUI EMCO Wrapper

#### Step 3.1: Add Initialization Script
```xml
<Script isActive="yes" isFolder="no">
  <name>LuminariGUI_EMCO_Init</name>
  <script><![CDATA[
GUI.EMCO = GUI.EMCO or {}

function GUI.EMCO:initialize()
  -- Load compatibility layer
  local EMCO_COMPAT = loadstring(EMCO_COMPATIBILITY_LAYER_CODE)()
  
  -- Create EMCO instance class (not require - embedded in XML)
  local EMCO = loadstring(EMCO_CORE_CODE)()
  
  -- Initialize EMCO in our existing chat container
  local emcoInstance = EMCO:new({
    name = "LuminariGUI_EMCO",
    x = 0,
    y = 0,
    width = "100%",
    height = "100%",
    
    -- Match existing YATCO tabs
    consoles = {"All", "Tell", "Chat", "Say", "Group", "Auction", "Congrats", "Wiz"},
    allTab = true,
    allTabName = "All",
    
    -- Visual settings to match LuminariGUI
    fontSize = getFontSize("main"),
    font = "Bitstream Vera Sans Mono",
    commandLine = false,  -- No command line
    
    -- Enable features matching YATCO config
    blink = true,
    timestamp = false,  -- YATCO default is false
    bufferSize = 10000,
    deleteLines = 500,
    blankLine = false,
    preserveBackground = true,
    gag = false,
    
    -- Colors to match theme
    consoleColor = "black",
    activeTabFGColor = "yellow",  -- Match YATCO
    inactiveTabFGColor = "white", -- Match YATCO
    activeTabBGColor = "<0,180,0>",
    inactiveTabBGColor = "<60,60,60>",
    
    -- Layout settings
    tabHeight = 25,
    gap = 2,
    wrapAt = getColumnCount("main"),
  }, GUI.chatContainerInner)  -- Use existing container
  
  -- Initialize compatibility wrapper
  demonnic.chat = EMCO_COMPAT.initialize(emcoInstance)
  
  -- Copy existing YATCO settings if they exist
  if GUI.EMCO.oldChat and GUI.EMCO.oldChat.config then
    local oldConfig = GUI.EMCO.oldChat.config
    demonnic.chat.config.soundEnabled = oldConfig.soundEnabled or false
    demonnic.chat.config.soundFile = oldConfig.soundFile or "audio/chat_sound.mp3"
    demonnic.chat.config.soundVolume = oldConfig.soundVolume or 100
    demonnic.chat.config.soundCooldown = oldConfig.soundCooldown or 0
  end
  
  -- Apply LuminariGUI styling
  GUI.EMCO:applyCustomStyling(emcoInstance)
  
  return true
end

function GUI.EMCO:applyCustomStyling(emco)
  -- Apply button image styling to tabs
  local tabCSS = [[
    font-family: Tahoma, Geneva, sans-serif;
    border-image: url(]] .. GUI.image_location .. [[buttons/button.png) 0 0 0 0 stretch stretch;
    border: 1px solid rgba(184, 115, 27, 0.5);
    border-radius: 3px 3px 0px 0px;
    padding: 2px;
    font-weight: bold;
  ]]
  
  emco:setActiveTabCSS(tabCSS .. "background-color: rgba(0, 255, 0, 0.3);")
  emco:setInactiveTabCSS(tabCSS .. "background-color: rgba(0, 0, 0, 0.3);")
end
]]></script>
</Script>
```

### Phase 4: Update Initialization System

#### Step 4.1: Modify demonnicOnStart() Function
Find the demonnicOnStart() function and replace with EMCO initialization:

```lua
function demonnicOnStart()
  if demonnic.chat.use then
    -- Check if we're using EMCO or YATCO
    if GUI.useEMCO then
      -- Store old chat reference if switching
      if demonnic.chat and not GUI.EMCO.initialized then
        GUI.EMCO.oldChat = demonnic.chat
      end
      
      -- Initialize EMCO
      if GUI.EMCO:initialize() then
        GUI.EMCO.initialized = true
        cecho("\n<green>EMCO chat system initialized<reset>\n")
      else
        cecho("\n<red>Failed to initialize EMCO<reset>\n")
        GUI.useEMCO = false
      end
    else
      -- Original YATCO initialization
      if GUI.chatContainerInner then
        demonnic.chat.useContainer = GUI.chatContainerInner
      elseif GUI.chatContainer then
        demonnic.chat.useContainer = GUI.chatContainer
      end
      
      local success, err = pcall(demonnic.chat.create, demonnic.chat)
      if not success then
        print(string.format("Error initializing chat system: %s", err))
      end
    end
  end
end
```

#### Step 4.2: Add Toggle Variable
Add to GUI initialization:
```lua
GUI.useEMCO = false  -- Start with YATCO, switch to true for EMCO
```

### Phase 5: Enable Safe Testing Mode

#### Step 5.1: DO NOT Deactivate YATCO Yet
Keep YATCO active for fallback - the compatibility layer handles coexistence

#### Step 5.2: All Triggers Work With Both Systems
All chat triggers remain unchanged - compatibility layer ensures they work with both YATCO and EMCO

#### Step 5.3: Add System Toggle Alias
```xml
<Alias isActive="yes" isFolder="no">
  <name>Toggle Chat System</name>
  <script>
function GUI.toggleChatSystem()
  if GUI.useEMCO then
    -- Switch to YATCO
    GUI.useEMCO = false
    cecho("\n<yellow>Switched to YATCO - restart Mudlet to apply<reset>\n")
  else
    -- Switch to EMCO
    GUI.useEMCO = true
    cecho("\n<green>Switched to EMCO - restart Mudlet to apply<reset>\n")
  end
  -- Save preference
  if GUI.toggles then
    GUI.toggles.useEMCO = GUI.useEMCO
    table.save(getMudletHomeDir() .. "/GUI.toggles.lua", GUI.toggles)
  end
end

GUI.toggleChatSystem()
  </script>
  <regex>^toggle chat system$</regex>
</Alias>
```

### Phase 6: Update Existing Aliases for Compatibility

#### Step 6.1: All Existing Aliases Work
The compatibility layer ensures all existing aliases continue to work:
- `gag chat` - Works with both systems
- `dblink` - Works with both systems  
- `dsound` - Works with both systems
- `set chat sound` - Works with both systems
- `fix chat` - Works with both systems

No changes needed to existing aliases!


### Phase 7: Enhanced Testing Protocol

#### Step 7.1: Pre-Migration Testing (With YATCO)
1. Start with `GUI.useEMCO = false` (YATCO mode)
2. Connect to game and verify all chat functionality works
3. Document current behavior:
   - [ ] All chat triggers capture correctly
   - [ ] Gag functionality works
   - [ ] Sound notifications play
   - [ ] Tab switching smooth
   - [ ] Channel colors display correctly

#### Step 7.2: EMCO Testing
1. Type `toggle chat system` to switch to EMCO
2. Restart Mudlet
3. Check error console for initialization issues
4. Perform same tests as Step 7.1:
   - [ ] All chat triggers capture correctly (via compatibility layer)
   - [ ] Gag functionality works
   - [ ] Sound notifications play
   - [ ] Tab switching smooth
   - [ ] Channel colors display correctly
   - [ ] Custom channel prefixes work

#### Step 7.3: Compatibility Testing
Test all existing commands work identically:
- [ ] `gag chat` - Toggle chat gagging
- [ ] `dblink` - Toggle tab blinking
- [ ] `dsound` - Toggle sound notifications
- [ ] `set chat sound on/off/test` - Sound configuration
- [ ] `fix chat` - Fix chat display issues
- [ ] `fix gui` - Ensure chat refreshes properly

#### Step 7.4: Performance Comparison
- [ ] Monitor memory usage over 1 hour session
- [ ] Check CPU usage during heavy chat activity
- [ ] Verify no lag or stuttering
- [ ] Test with 1000+ lines in each tab

#### Step 7.5: Edge Case Testing
- [ ] Rapid tab switching
- [ ] Multiple channels firing simultaneously
- [ ] Long messages wrapping correctly
- [ ] Special characters and color codes
- [ ] Adjustable Container resize/move

### Phase 8: Finalization (After 1 Week Stable)

#### Step 8.1: Make EMCO Default
After 1 week of stable operation:
1. Change `GUI.useEMCO = true` as default
2. Keep YATCO code but set `isActive="no"`
3. Keep compatibility layer active

#### Step 8.2: Optimize Configuration
1. Fine-tune EMCO settings based on user feedback
2. Document any user-visible changes
3. Update README with EMCO information

#### Step 8.3: Long-term Cleanup (After 1 Month)
Only after extended stable operation:
1. Remove YATCO script groups
2. Integrate compatibility layer features directly
3. Simplify initialization code

## Enhanced Rollback Plan

### Immediate Rollback (Any Critical Issue)
1. Type `toggle chat system` to switch back to YATCO
2. Restart Mudlet
3. Everything returns to normal - no code changes needed

### Git Rollback (If Files Corrupted)
```bash
git checkout yatco-final-v2.0.4.016
```

### Debugging Support
The compatibility layer provides extensive debugging:
- All YATCO API calls are intercepted and logged if debug enabled
- Can trace exact differences in behavior
- Error messages indicate whether issue is in EMCO or compatibility layer

### Progressive Rollback
1. **First**: Try toggling back to YATCO (instant fix)
2. **Second**: Disable specific EMCO features causing issues
3. **Third**: Use git rollback only if file corruption

## Success Criteria

The migration is considered successful when:
- [ ] All existing chat channels work identically to YATCO
- [ ] Zero changes required to triggers or aliases
- [ ] No errors in Mudlet console during normal operation
- [ ] Performance is equal or better than YATCO
- [ ] All custom features work exactly as before:
  - [ ] Chat gagging with `gag chat`
  - [ ] Tab blinking with `dblink`
  - [ ] Sound notifications with `dsound`
  - [ ] Channel color prefixes
- [ ] Adjustable Container integration works smoothly
- [ ] Users can switch between systems without issues
- [ ] System runs stable for 1 week minimum
- [ ] Memory usage stays consistent over long sessions

## Post-Installation Benefits

Once EMCO is successfully installed:
- Dynamic tab management
- Better memory management with buffer limits
- Built-in logging capabilities
- More configuration options
- Easier to extend with new features
- Active development and community support

## Key Improvements in This Plan

1. **Compatibility Layer**: Maintains 100% YATCO API compatibility
2. **Zero Breaking Changes**: All triggers and aliases work unchanged
3. **Safe Testing**: Toggle between systems without code changes
4. **Progressive Migration**: Test thoroughly before committing
5. **Enhanced Rollback**: Instant switch back to YATCO if needed

## Implementation Notes

- The compatibility layer (EMCO_COMPATIBILITY_LAYER.lua) is the key to success
- No triggers need modification - they continue using `demonnic.chat:append()`
- All configuration is mapped automatically
- Sound support is maintained in the compatibility layer
- Custom features like channel colors work through the wrapper

## Critical Files

1. **YATCO_AUDIT.md** - Complete reference documentation
2. **EMCO_API_ANALYSIS.md** - API differences and mapping
3. **EMCO_COMPATIBILITY_LAYER.lua** - The compatibility wrapper
4. **This document** - Updated installation plan

Keep all documentation for reference during implementation.