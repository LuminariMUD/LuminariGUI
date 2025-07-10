# LuminariGUI Troubleshooting Guide

This guide provides systematic troubleshooting solutions for LuminariGUI, organized from simple fixes for casual users to advanced diagnostics for technical users.

## Table of Contents

- [Quick Fixes (Start Here)](#quick-fixes-start-here)
- [Error Classification System](#error-classification-system)
- [Installation Issues](#installation-issues)
- [Runtime Problems](#runtime-problems)
- [Component-Specific Troubleshooting](#component-specific-troubleshooting)
- [Performance Issues](#performance-issues)
- [Advanced Diagnostics](#advanced-diagnostics)
- [Recovery Procedures](#recovery-procedures)

---

## Quick Fixes (Start Here)

### 🚀 Most Common Issues (90% of problems)

Try these solutions first - they resolve most issues:

#### **Problem: LuminariGUI won't install**
```
✅ Quick Fix:
1. Close Mudlet completely
2. Download fresh copy of LuminariGUI.mpackage
3. Right-click → "Run as Administrator" (Windows) or use sudo (Linux)
4. Try installation again
```

#### **Problem: UI elements are missing or invisible**
```
✅ Quick Fix:
1. Type in Mudlet: lua LuminariGUI.reload()
2. If still broken: restart Mudlet
3. Check connection to MUD server
4. Verify MSDP is enabled: send("config +msdp")
```

#### **Problem: Chat tabs not working**
```
✅ Quick Fix:
1. Check YATCO is installed: lua print(yatco)
2. Restart Mudlet if YATCO missing
3. Reconfigure channels: see CONFIGURATION.md
```

#### **Problem: Gauges not updating**
```
✅ Quick Fix:
1. Verify MSDP connection: lua display(msdp)
2. If empty, enable MSDP: send("config +msdp")
3. Wait 30 seconds for data sync
4. Restart if still broken
```

#### **Problem: Map not displaying**
```
✅ Quick Fix:
1. Enable mapping: Settings → Mapper → Enable
2. Download area map from MUD
3. Restart Mudlet
4. Check map window is open: View → Show Map
```

---

## Error Classification System

Understanding error types helps choose the right solution:

```
🔍 ERROR IDENTIFICATION FLOWCHART

Error Occurs
├── Installation Phase?
│   ├── Yes → [Installation Issues](#installation-issues)
│   └── No → Continue below
├── During Startup?
│   ├── Yes → [Runtime Problems](#runtime-problems)
│   └── No → Continue below
├── Specific Component?
│   ├── Chat → [YATCO Issues](#yatco-chat-system)
│   ├── Gauges → [UI Component Issues](#ui-component-issues)
│   ├── Map → [Mapping System Issues](#mapping-system-issues)
│   └── Performance → [Performance Issues](#performance-issues)
└── Unknown → [Advanced Diagnostics](#advanced-diagnostics)
```

### Error Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| 🟢 **Minor** | Cosmetic issues, minor functionality | Optional fix, workaround available |
| 🟡 **Moderate** | Reduced functionality, some features broken | Recommended fix, impacts usability |
| 🔴 **Severe** | Major features broken, unstable operation | Immediate fix required |
| ⚫ **Critical** | Complete failure, unusable system | Emergency recovery procedures |

---

## Installation Issues

### Package Installation Failures

#### **Symptom: "Package could not be installed" error**

**Skill Level: Beginner**
```
Solution Steps:
1. Check file integrity
   - Re-download LuminariGUI.mpackage
   - Verify file size (~200KB)
   - Check download completed fully

2. Try alternative installation
   - Use manual XML installation method
   - See DEPLOYMENT.md → Manual Installation

3. Check permissions
   - Windows: Run Mudlet as Administrator
   - macOS: Check Security & Privacy settings
   - Linux: Verify user permissions
```

**Skill Level: Advanced**
```lua
-- Debug package installation
lua 
local path = "/path/to/LuminariGUI.mpackage"
local file = io.open(path, "rb")
if file then
    print("File accessible:", path)
    local size = file:seek("end")
    print("File size:", size, "bytes")
    file:close()
else
    print("Cannot access file:", path)
end
```

### Dependency Issues

#### **Missing YATCO Dependency**

**Symptoms:**
- Chat tabs missing
- Error: "YATCO not found"
- Console shows script errors

**Solutions:**
```
Beginner Fix:
1. Download YATCO separately
2. Install YATCO before LuminariGUI
3. Reinstall LuminariGUI

Advanced Fix:
```lua
-- Check YATCO installation
lua
if yatco then
    print("YATCO version:", yatco.version or "unknown")
else
    print("YATCO not installed - install from Mudlet Package Manager")
end
```

### Permission and Path Issues

#### **Windows-Specific**
```powershell
# Check Mudlet installation path
Get-ChildItem "C:\Program Files\Mudlet" -Recurse | Where-Object {$_.Name -like "*profile*"}

# Verify user permissions
icacls "%APPDATA%\Mudlet" /T
```

#### **Linux-Specific**
```bash
# Check profile directory permissions
ls -la ~/.local/share/Mudlet/profiles/

# Fix permissions if needed
chmod -R 755 ~/.local/share/Mudlet/profiles/
```

---

## Runtime Problems

### Startup Failures

#### **LuminariGUI loads but doesn't function**

**Diagnosis Steps:**
1. **Check Error Console**
   ```
   View → Show Errors (Ctrl+E)
   Look for red error messages
   ```

2. **Test Core Functions**
   ```lua
   -- Test basic functionality
   lua print("LuminariGUI object:", type(LuminariGUI))
   lua print("Background created:", LuminariGUI.background ~= nil)
   lua print("MSDP working:", msdp ~= nil and next(msdp) ~= nil)
   ```

3. **Common Fixes**
   ```lua
   -- Reload package
   lua uninstallPackage("LuminariGUI")
   lua installPackage(getMudletHomeDir().."/LuminariGUI.xml")
   
   -- Reset configuration
   lua LuminariGUI.resetConfig()
   ```

### MSDP Connection Problems

#### **No MSDP Data Received**

**Beginner Troubleshooting:**
```
1. Enable MSDP on server:
   send("config +msdp")
   
2. Wait 30 seconds for sync

3. Test reception:
   Type: lua display(msdp)
   Should show data table

4. If empty, contact server admin
```

**Advanced Diagnostics:**
```lua
-- MSDP debug mode
lua
registerAnonymousEventHandler("msdp", function()
    print("MSDP received:", table.concat(msdp_vars, ", "))
end)

-- Test specific MSDP variables
lua
local required_vars = {"HEALTH", "MANA", "MOVEMENT", "HEALTH_MAX", "MANA_MAX", "MOVEMENT_MAX"}
for _, var in ipairs(required_vars) do
    print(var, ":", msdp[var] or "MISSING")
end
```

### Script Execution Errors

#### **Lua Runtime Errors**

**Error Pattern Recognition:**
```
Common Error Types:
├── "attempt to index nil value" → Missing object reference
├── "attempt to call nil function" → Missing function/method
├── "syntax error" → Code formatting issue
└── "bad argument" → Wrong data type passed
```

**Debugging Process:**
```lua
-- Enable detailed error reporting
lua
function LuminariGUI.errorHandler(err)
    print("LuminariGUI Error:", err)
    print("Stack trace:", debug.traceback())
end

-- Set error handler
lua LuminariGUI.onError = LuminariGUI.errorHandler
```

---

## Component-Specific Troubleshooting

### YATCO Chat System

#### **Chat Tabs Not Appearing**

**Skill Level: Beginner**
```
Quick Diagnostics:
1. Check YATCO installation
   - Packages → Package Manager
   - Look for "YATCO" in installed packages

2. Verify chat configuration
   - See if channels are configured
   - Check server supports channels

3. Restart sequence
   - Disconnect from MUD
   - Restart Mudlet
   - Reconnect and test
```

**Skill Level: Advanced**
```lua
-- YATCO diagnostic script
lua
if yatco then
    print("YATCO installed:", yatco.version)
    print("Chat windows:", table.size(yatco.windows))
    for name, window in pairs(yatco.windows) do
        print("  Window:", name, "Visible:", window:isVisible())
    end
else
    print("YATCO not found - check installation")
end

-- Test chat configuration
lua
for channel, config in pairs(LuminariGUI.chat_config or {}) do
    print("Channel:", channel, "Enabled:", config.enabled)
end
```

#### **Chat Messages Not Routing**

**Common Causes:**
1. **Trigger Conflicts**: Other packages intercepting messages
2. **Channel Configuration**: Wrong channel names/patterns
3. **Server Changes**: MUD changed channel formats

**Solutions:**
```lua
-- Debug message routing
lua
function LuminariGUI.debugChat(message)
    print("Received message:", message)
    print("Active triggers:", table.size(getTriggerTable()))
end

-- Test specific channel
lua LuminariGUI.testChannel("gossip", "This is a test message")
```

### UI Component Issues

#### **Gauges Not Updating**

**Visual Diagnostic Checklist:**
- [ ] Gauges visible on screen?
- [ ] Numbers changing when stats change?
- [ ] Colors updating correctly?
- [ ] Proper positioning/scaling?

**Systematic Testing:**
```lua
-- Test gauge system
lua
local gauges = {"health", "mana", "movement"}
for _, gauge in ipairs(gauges) do
    local obj = LuminariGUI.gauges[gauge]
    if obj then
        print(gauge, "gauge: OK")
        print("  Current value:", obj:getValue())
        print("  Max value:", obj:getMaxValue())
    else
        print(gauge, "gauge: MISSING")
    end
end
```

**Manual Gauge Update:**
```lua
-- Force gauge refresh
lua
LuminariGUI.updateGauges()

-- Test with fake data
lua
LuminariGUI.gauges.health:setValue(50, 100)  -- 50/100 HP
LuminariGUI.gauges.mana:setValue(75, 150)    -- 75/150 MP
```

#### **Background/UI Layout Problems**

**Common Issues:**
- Elements overlapping
- Gauges positioned incorrectly  
- Text unreadable/cut off
- Resolution scaling problems

**Resolution-Based Fixes:**
```lua
-- Check current resolution
lua
local width, height = getMainWindowSize()
print("Screen resolution:", width .. "x" .. height)

-- Reset UI positioning
lua LuminariGUI.resetUIPositions()

-- Scale for different resolutions
lua
if width < 1024 then
    LuminariGUI.setUIScale(0.8)  -- Smaller screens
elseif width > 1920 then
    LuminariGUI.setUIScale(1.2)  -- Larger screens
end
```

### Mapping System Issues

#### **Map Not Displaying**

**Step-by-Step Diagnosis:**
1. **Verify Mapper Enabled**
   ```
   Settings → Mapper → Enable mapper
   ```

2. **Check Map Window**
   ```
   View → Show Map Window
   Window should appear with controls
   ```

3. **Test Map Data**
   ```lua
   -- Check room data
   lua
   local room_id = getRoomID()
   if room_id then
       print("Current room:", room_id)
       print("Room name:", getRoomName(room_id))
   else
       print("No room data - map not loaded")
   end
   ```

4. **Load Map Data**
   ```
   If no map data exists:
   1. Download map from MUD website
   2. Or use: SPEEDWALK → Create Map
   3. Walk around to generate map data
   ```

#### **Map Display Corruption**

**Symptoms:**
- Map shows garbled graphics
- Rooms displayed incorrectly
- Navigation arrows missing

**Recovery Steps:**
```lua
-- Reset map display
lua
resetProfile()  -- WARNING: Resets ALL settings
-- OR safer option:
centerview(getRoomID())
setMapZoom(1.0)
```

---

## Performance Issues

### High CPU Usage

#### **Identification**
```
Windows: Task Manager → Processes → Look for "mudlet.exe"
macOS: Activity Monitor → CPU tab → Search "Mudlet"
Linux: top or htop → Look for mudlet process
```

#### **Common Causes & Solutions**

**1. Excessive MSDP Updates**
```lua
-- Reduce MSDP update frequency
lua
LuminariGUI.msdp_throttle = 100  -- Update every 100ms instead of every packet
```

**2. Too Many UI Updates**
```lua
-- Optimize gauge updates
lua
LuminariGUI.gauge_update_interval = 200  -- Update every 200ms
```

**3. Debug Mode Enabled**
```lua
-- Disable debug output
lua
LuminariGUI.debug = false
LuminariGUI.verbose_logging = false
```

### Memory Leaks

#### **Detection**
```lua
-- Monitor memory usage
lua
function LuminariGUI.memoryReport()
    collectgarbage("collect")  -- Force garbage collection
    local mem = collectgarbage("count")
    print("Memory usage:", math.floor(mem), "KB")
    return mem
end

-- Run periodically
lua tempTimer(5, [[ LuminariGUI.memoryReport() ]])
```

#### **Common Leak Sources**
1. **Event Handlers**: Not properly unregistered
2. **Timers**: Not cleaned up
3. **Large Data Structures**: Not cleared

**Cleanup Procedures:**
```lua
-- Clean up event handlers
lua
for _, id in ipairs(LuminariGUI.event_handlers) do
    killAnonymousEventHandler(id)
end
LuminariGUI.event_handlers = {}

-- Clean up timers
lua
for _, id in ipairs(LuminariGUI.timers) do
    killTimer(id)
end
LuminariGUI.timers = {}
```

### UI Lag/Stuttering

#### **Diagnostic Tools**
```lua
-- Performance profiler
lua
local start_time = getStopWatchTime("ui_update")
-- ... UI update code ...
local end_time = getStopWatchTime("ui_update")
print("UI update took:", end_time - start_time, "ms")
```

#### **Optimization Strategies**
```lua
-- Reduce update frequency for non-critical elements
lua
LuminariGUI.background_update_interval = 1000  -- 1 second
LuminariGUI.affect_update_interval = 2000      -- 2 seconds

-- Batch UI updates
lua
function LuminariGUI.batchUIUpdate()
    -- Update all elements at once instead of individually
    LuminariGUI.updateGauges()
    LuminariGUI.updateAffects()
    LuminariGUI.updateChat()
end
```

---

## Advanced Diagnostics

### Debug Mode Activation

#### **Enable Comprehensive Logging**
```lua
-- Full debug mode
lua
LuminariGUI.debug = true
LuminariGUI.verbose_logging = true
LuminariGUI.log_level = "DEBUG"

-- Create debug log file
LuminariGUI.enableFileLogging(getMudletHomeDir() .. "/luminari_debug.log")
```

#### **Debug Information Collection**
```lua
-- System information dump
lua
function LuminariGUI.systemDiagnostic()
    local info = {
        mudlet_version = getMudletVersion(),
        os_name = getOS(),
        profile_name = getProfileName(),
        screen_size = getMainWindowSize(),
        msdp_status = msdp ~= nil and "Connected" or "Disconnected",
        yatco_status = yatco ~= nil and "Installed" or "Missing",
        package_version = LuminariGUI.version or "Unknown",
        memory_usage = collectgarbage("count") .. " KB"
    }
    
    print("=== LuminariGUI System Diagnostic ===")
    for key, value in pairs(info) do
        print(key .. ":", value)
    end
    
    return info
end

-- Run diagnostic
lua LuminariGUI.systemDiagnostic()
```

### Network Diagnostics

#### **MSDP Connection Analysis**
```lua
-- MSDP packet monitor
lua
local msdp_packets = 0
local msdp_bytes = 0

registerAnonymousEventHandler("msdp", function()
    msdp_packets = msdp_packets + 1
    msdp_bytes = msdp_bytes + string.len(table.concat(msdp_vars, ""))
    
    if msdp_packets % 10 == 0 then
        print("MSDP Stats: ", msdp_packets, "packets,", msdp_bytes, "bytes")
    end
end)
```

#### **Connection Quality Testing**
```lua
-- Lag detection
lua
function LuminariGUI.lagTest()
    local start_time = os.clock()
    send("time")  -- Send command to server
    
    -- Register response handler
    tempTrigger("The time is", function()
        local end_time = os.clock()
        local lag = (end_time - start_time) * 1000
        print("Server response time:", math.floor(lag), "ms")
    end)
end
```

### Package Conflict Detection

#### **Identify Conflicting Packages**
```lua
-- List all installed packages
lua
function LuminariGUI.packageAudit()
    print("=== Installed Packages ===")
    
    local packages = getPackages()
    for _, package in ipairs(packages) do
        print("Package:", package)
        
        -- Check for potential conflicts
        if package:lower():find("gui") or package:lower():find("ui") then
            print("  → Potential UI conflict risk")
        end
        
        if package:lower():find("chat") or package:lower():find("yatco") then
            print("  → Potential chat conflict risk")
        end
    end
end

lua LuminariGUI.packageAudit()
```

#### **Event Handler Conflicts**
```lua
-- Check event handler registration
lua
function LuminariGUI.eventAudit()
    print("=== Event Handler Analysis ===")
    
    local events = {"msdp", "sysDataSendRequest", "sysConnectionEvent"}
    for _, event in ipairs(events) do
        local handlers = getEventHandlers(event)
        if handlers then
            print("Event:", event, "Handlers:", #handlers)
            if #handlers > 3 then
                print("  → Warning: Many handlers registered")
            end
        end
    end
end
```

---

## Recovery Procedures

### Emergency Recovery

#### **Complete System Reset**
Use only when everything else fails:

```lua
-- EMERGENCY RESET - USE WITH CAUTION
lua
function LuminariGUI.emergencyReset()
    print("WARNING: This will reset ALL LuminariGUI settings!")
    print("Type: LuminariGUI.confirmReset() to proceed")
end

function LuminariGUI.confirmReset()
    -- Uninstall package
    uninstallPackage("LuminariGUI")
    
    -- Clear all stored data
    clearConfig("LuminariGUI")
    
    -- Reset UI elements
    resetProfile()  -- WARNING: Resets entire Mudlet profile
    
    print("Emergency reset complete. Restart Mudlet and reinstall LuminariGUI.")
end
```

#### **Selective Component Reset**
```lua
-- Reset specific components only
lua
function LuminariGUI.resetComponent(component)
    local resetters = {
        gauges = function() 
            LuminariGUI.gauges = {}
            LuminariGUI.createGauges()
        end,
        
        chat = function()
            if yatco then
                yatco.reset()
            end
            LuminariGUI.setupChat()
        end,
        
        background = function()
            if LuminariGUI.background then
                LuminariGUI.background:hide()
            end
            LuminariGUI.createBackground()
        end,
        
        msdp = function()
            LuminariGUI.msdp_handlers = {}
            LuminariGUI.setupMSDP()
        end
    }
    
    if resetters[component] then
        resetters[component]()
        print("Reset component:", component)
    else
        print("Available components:", table.concat(table.keys(resetters), ", "))
    end
end

-- Usage: LuminariGUI.resetComponent("gauges")
```

### Configuration Corruption Recovery

#### **Backup and Restore**
```lua
-- Create configuration backup
lua
function LuminariGUI.backupConfig()
    local config = getConfig("LuminariGUI")
    local backup_file = getMudletHomeDir() .. "/luminari_config_backup.json"
    
    local file = io.open(backup_file, "w")
    if file then
        file:write(yajl.to_string(config))
        file:close()
        print("Configuration backed up to:", backup_file)
    else
        print("Failed to create backup file")
    end
end

-- Restore from backup
lua
function LuminariGUI.restoreConfig()
    local backup_file = getMudletHomeDir() .. "/luminari_config_backup.json"
    
    local file = io.open(backup_file, "r")
    if file then
        local content = file:read("*all")
        file:close()
        
        local config = yajl.to_value(content)
        setConfig("LuminariGUI", config)
        print("Configuration restored from backup")
        return true
    else
        print("No backup file found")
        return false
    end
end
```

### Data Recovery

#### **MSDP Data Recovery**
```lua
-- Recover lost MSDP variables
lua
function LuminariGUI.recoverMSDP()
    print("Attempting MSDP recovery...")
    
    -- Request all known variables
    local variables = {
        "HEALTH", "HEALTH_MAX", "MANA", "MANA_MAX", 
        "MOVEMENT", "MOVEMENT_MAX", "LEVEL", "EXPERIENCE",
        "ROOM_NAME", "ROOM_EXITS", "ROOM_VNUM"
    }
    
    for _, var in ipairs(variables) do
        sendMSDP(var)
    end
    
    print("MSDP recovery requests sent")
end
```

#### **UI State Recovery**
```lua
-- Rebuild UI from scratch
lua
function LuminariGUI.rebuildUI()
    print("Rebuilding UI components...")
    
    -- Clear existing UI
    if LuminariGUI.background then
        LuminariGUI.background:hide()
    end
    
    -- Recreate core components
    LuminariGUI.createBackground()
    LuminariGUI.createGauges()
    LuminariGUI.setupChat()
    LuminariGUI.setupMap()
    
    print("UI rebuild complete")
end
```

---

## Prevention and Maintenance

### Regular Maintenance Tasks

#### **Weekly Maintenance**
```lua
-- Run weekly maintenance
lua
function LuminariGUI.weeklyMaintenance()
    print("=== LuminariGUI Weekly Maintenance ===")
    
    -- Clean up memory
    collectgarbage("collect")
    print("Memory cleaned:", collectgarbage("count"), "KB")
    
    -- Backup configuration
    LuminariGUI.backupConfig()
    
    -- Check for updates
    LuminariGUI.checkVersion()
    
    -- Validate configuration
    LuminariGUI.validateConfig()
    
    print("Maintenance complete")
end
```

#### **Log Rotation**
```lua
-- Rotate debug logs
lua
function LuminariGUI.rotateLogs()
    local log_file = getMudletHomeDir() .. "/luminari_debug.log"
    local backup_file = getMudletHomeDir() .. "/luminari_debug.log.old"
    
    -- Move current log to backup
    os.rename(log_file, backup_file)
    
    print("Debug logs rotated")
end
```

### Health Checks

#### **System Health Monitor**
```lua
-- Automated health check
lua
function LuminariGUI.healthCheck()
    local issues = {}
    
    -- Check core components
    if not LuminariGUI.background then
        table.insert(issues, "Background missing")
    end
    
    if not LuminariGUI.gauges or table.size(LuminariGUI.gauges) == 0 then
        table.insert(issues, "Gauges missing")
    end
    
    if not msdp or table.size(msdp) == 0 then
        table.insert(issues, "MSDP not working")
    end
    
    if not yatco then
        table.insert(issues, "YATCO missing")
    end
    
    -- Report results
    if #issues == 0 then
        print("✅ Health Check: All systems OK")
    else
        print("⚠️ Health Check Issues Found:")
        for _, issue in ipairs(issues) do
            print("  -", issue)
        end
    end
    
    return #issues == 0
end

-- Run health check every hour
lua tempTimer(3600, [[ LuminariGUI.healthCheck() ]])
```

---

## Getting Additional Help

### Documentation Resources

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Installation and setup procedures
- **[CONFIGURATION.md](CONFIGURATION.md)**: Advanced configuration options  
- **[API.md](API.md)**: Developer API and scripting reference
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development and contribution guidelines

### Community Support

- **GitHub Issues**: Report bugs and request features
- **MUD Forums**: Community discussions and help
- **Discord/IRC**: Real-time support channels
- **Documentation Wiki**: Community-maintained guides

### Professional Support

For complex issues or custom modifications:
- Contact package maintainer
- Professional Mudlet consulting services
- Custom development services

### Reporting Bugs

When reporting issues, include:

```lua
-- Generate bug report
lua
function LuminariGUI.generateBugReport()
    print("=== LuminariGUI Bug Report ===")
    
    -- System info
    LuminariGUI.systemDiagnostic()
    
    -- Error logs
    print("\nRecent Errors:")
    -- Include any error messages from console
    
    -- Steps to reproduce
    print("\nSteps to Reproduce:")
    print("1. [Describe what you were doing]")
    print("2. [What happened]")
    print("3. [What you expected]")
    
    print("\nPlease copy this output when reporting bugs")
end
```

---

*This troubleshooting guide is part of the LuminariGUI documentation suite. For the most current version and additional resources, visit the official repository.*