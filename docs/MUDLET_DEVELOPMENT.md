# LuminariGUI Development Guide

This document outlines the development workflow, architecture, and best practices for the LuminariGUI project.

> **Mudlet version compatibility:** Mudlet 4.20 migrated to Qt6 and 4.21 changed label/callback internals and MSDP negotiation. If the package worked on an older Mudlet and misbehaves on a newer one, read **[MUDLET_COMPATIBILITY.md](MUDLET_COMPATIBILITY.md)** first — it has a version-by-version breakdown and a triage checklist.

## Project Architecture

### Source-to-Build Architecture
**LuminariGUI is assembled from modular XML fragments.** Edit source files in `theGUI/src/`, **not** `LuminariGUI.xml` directly — the latter is a build output and will be overwritten.

```
theGUI/
├── build.py          # Build script (XML assembly)
├── package.py        # Package manager (.mpackage creation, releases)
├── build.yaml        # Manifest (fragment list, version)
├── skeleton.xml      # Package structure template
└── src/              # SOURCE OF TRUTH
    ├── triggers/     # Trigger definitions
    ├── aliases/      # Alias definitions
    ├── scripts/      # Lua scripts
    └── keys/         # Key bindings
```

-   **Source of Truth**: the fragments under `theGUI/src/`, listed in `theGUI/build.yaml`.
-   **Build Output**: `LuminariGUI.xml`, assembled by `build.py`. Each build auto-increments the version in `build.yaml` and archives the previous XML to `docs/archive/`.
-   **Embedded Lua**: Lua scripts are embedded inside the XML fragments.
-   **Python Toolchain**: custom Python scripts (see [PYTHON_TOOLS.md](PYTHON_TOOLS.md)) assemble, validate, test, and release the package.

Fragments are named `NN_descriptive_name.xml`, where `NN` is `00`–`09` for core/init, `10`–`19` for major subsystems, and `20+` for extensions.

### Workflow
1.  **Edit**: Change fragments in `theGUI/src/`.
2.  **Validate**: `python3 theGUI/build.py --validate` (no changes written) and `python3 scripts/validate_package.py`.
3.  **Build**: `python3 theGUI/build.py` to assemble `LuminariGUI.xml`.
4.  **Test**: `python3 tests/run_tests.py`.
5.  **Manual test**: import `LuminariGUI.xml` into Mudlet.
6.  **Commit** the source fragments, `theGUI/build.yaml`, the built
    `LuminariGUI.xml`, and any newly generated tracked archive.
7.  **Preview**: `python3 theGUI/package.py release --dry-run`.
8.  **Publish**: `python3 theGUI/package.py release`. The command commits the
    final release artifacts, merges them into `master`, atomically pushes
    `master`, the release branch, and tag to `origin`, and verifies the remote
    refs. It then publishes the GitHub Release page with the `.mpackage` and
    JSON metadata attached and verifies both assets. It never treats local
    commits as a completed release.
9.  **Verify**: independently inspect the remote refs and GitHub Release before
    handoff. See [PYTHON_TOOLS.md](PYTHON_TOOLS.md#creating-a-release).

Additional build modes: `--diff` and `--stats` are read-only; `--extract`
overwrites fragments and `build.yaml`, while `--watch` immediately builds and
then rebuilds/version-bumps on every change. Use the mutating modes only when
that behavior is intended.

---

## General Mudlet Development Best Practices

*(The following sections provide general advice for Mudlet package development)*

## Table of Contents
1. [Foundation: Understanding Mudlet Packages](#foundation)
2. [Development Methods: Choosing Your Approach](#development-methods)
3. [Project Architecture & Best Practices](#architecture)
4. [Core Development Principles](#core-principles)
5. [Advanced Features & Integration](#advanced-features)
6. [Distribution & Maintenance](#distribution)
7. [Professional Workflow & Tools](#professional-workflow)

## Foundation: Understanding Mudlet Packages {#foundation}

A Mudlet package is a **collection of triggers, aliases, timers, scripts, keybindings, and resources** bundled into a single `.mpackage` file . These packages are essentially **ZIP archives containing XML configuration data and optional assets** like images, sounds, and fonts .

### Key Components of a Package

- **Scripts**: Core functionality written in Lua
- **Triggers**: Pattern matching for game output
- **Aliases**: Custom commands for players
- **Timers**: Scheduled actions and updates
- **Keybindings**: Keyboard shortcuts
- **GUI Elements**: Windows, labels, gauges
- **Resources**: Images, sounds, fonts, and other assets

## Development Methods: Choosing Your Approach {#development-methods}

> **Note:** LuminariGUI uses **neither** of the two methods below — it uses its own Python source-to-build toolchain (`theGUI/build.py` + `theGUI/package.py`), described above. The following is background on the ecosystem's standard options, useful context when reading other packages' source or Mudlet's own documentation.

### Method 1: Mudlet's Built-in Package Exporter (Beginner-Friendly)

The **Package Exporter** is accessible from Mudlet's toolbar and provides a graphical interface . This method is ideal for simple packages and quick prototypes.

**Essential Metadata Configuration:**
- **Package Name**: Choose unique, descriptive names to avoid conflicts 
- **Version**: Use semantic versioning (e.g., 1.0.0)
- **Author**: Your name or team information
- **Description**: Support GitHub-flavored markdown for formatting 
- **Icon**: 512x512 pixels recommended 
- **Dependencies**: List required packages like `generic_mapper` 
- **Assets**: Declare all external files for proper bundling 

**Asset Declaration Example:**
```lua
-- Reference bundled assets correctly
setBackgroundImage("my health label", getMudletHomeDir().."/sipper/health.png")
```

**The `.mpackage` format and `config.lua`:**

An `.mpackage` is a ZIP archive containing the package XML, a `config.lua` manifest, and any bundled assets. The authoritative field list — taken from Mudlet's own exporter (`src/dlgPackageExporter.cpp`, `writeConfigFile`) — is:

| Field | Notes |
|---|---|
| `mpackage` | Package name (the internal identifier) |
| `author` | |
| `icon` | Icon *filename* as bundled in the archive |
| `title` | |
| `description` | Supports GitHub-flavored markdown |
| `version` | |
| `helpURL` | Normalized to `https://` if no scheme given |
| `dependencies` | **A comma-separated string**, not a Lua table |
| `created` | ISO-8601 timestamp |

```lua
mpackage = "MyMudPackage"
author = "YourName"
title = "My MUD Enhancement Package"
version = "1.0.0"
dependencies = "generic_mapper"
created = "2026-07-31"
```

Since Mudlet 4.20 the exporter no longer enforces required fields, and packages without an icon no longer get a default one.

### Method 2: Muddler Build Tool (Professional Development)

**Muddler** is a sophisticated build tool that enables **version control integration, IDE support, and standardized project structure** . It's built with Groovy and requires Java 1.8+ .

**Setup Process:**
1. Install Java 1.8 or higher 
2. Download Muddler from [GitHub releases](https://github.com/demonnic/muddler/releases) 
3. Run `muddle --generate` for basic structure or `muddle --default` for full project 

**Standard Project Structure:**
```
MyMudPackage/
├── mfile                    # Package configuration (JSON)
├── src/
│   ├── aliases/
│   │   └── MyPackage/
│   │       ├── aliases.json
│   │       └── commands.lua
│   ├── triggers/
│   │   └── MyPackage/
│   │       ├── triggers.json
│   │       └── handlers.lua
│   ├── scripts/
│   │   └── MyPackage/
│   │       └── main.lua
│   ├── timers/
│   ├── keybindings/
│   └── resources/
│       ├── images/
│       ├── sounds/
│       └── fonts/
└── build/                   # Generated packages
```

**Muddler Configuration (mfile):**
```json
{
  "package": "MyMudPackage",
  "title": "My MUD Enhancement Package",
  "description": "Enhances gameplay with custom features",
  "version": "1.0.0",
  "author": "YourName",
  "icon": "resources/icon.png",
  "dependencies": ["generic_mapper"],
  "outputFile": true
}
```

**Token Replacement Feature:**
Muddler supports dynamic token replacement :
```lua
-- In your code:
require("@PKGNAME@.module")
-- Becomes:
require("MyMudPackage.module")
```

## Project Architecture & Best Practices {#architecture}

### Namespace Management

**Always use a unique namespace** to prevent conflicts :

```lua
-- Initialize namespace safely
MyMudPackage = MyMudPackage or {
    isInitialized = false,
    version = "1.0.0"
}

-- Guard against re-initialization
if not MyMudPackage.isInitialized then
    MyMudPackage.config = {}
    MyMudPackage.data = {}
    MyMudPackage.gui = {}
    MyMudPackage.isInitialized = true
end
```

### Modular Design Principles 

Structure your package into logical modules:

```lua
-- Core module
MyMudPackage.Core = {
    initialize = function()
        MyMudPackage.Config.load()
        MyMudPackage.GUI.create()
        MyMudPackage.Events.register()
    end,
    
    shutdown = function()
        MyMudPackage.Config.save()
        MyMudPackage.GUI.cleanup()
        MyMudPackage.Events.unregister()
    end
}

-- Configuration module
MyMudPackage.Config = {
    defaults = {
        autoMap = true,
        theme = "dark",
        fontSize = 12
    },
    
    load = function()
        local configPath = getMudletHomeDir() .. "/MyMudPackage_config.lua"
        local loaded = {}
        table.load(configPath, loaded)
        MyMudPackage.settings = table.update(MyMudPackage.Config.defaults, loaded or {})
    end,
    
    save = function()
        local configPath = getMudletHomeDir() .. "/MyMudPackage_config.lua"
        table.save(configPath, MyMudPackage.settings)
    end
}
```

### Event-Driven Architecture 

Use custom events for loose coupling:

```lua
-- Raise custom events
function MyMudPackage.updateHealth(current, max)
    MyMudPackage.health = {current = current, max = max}
    raiseEvent("MyMudPackage.healthChanged", current, max)
end

-- Allow other scripts to respond
registerAnonymousEventHandler("MyMudPackage.healthChanged", function(event, current, max)
    -- Update displays, trigger alerts, etc.
    MyMudPackage.GUI.updateHealthBar(current, max)
end)
```

## Core Development Principles {#core-principles}

### Lua Best Practices 

**1. Always Use Local Variables:**
```lua
-- BAD: Global pollution
function processMessage(msg)
    formatted = "[" .. os.date() .. "] " .. msg  -- Global!
    cecho(formatted)
end

-- GOOD: Local scope
function processMessage(msg)
    local formatted = "[" .. os.date() .. "] " .. msg
    cecho(formatted)
end
```

**2. Avoid Direct `_G` Access:**
```lua
-- BAD: Risk of overwriting core functions
_G["echo"] = function() end  -- Breaks Mudlet!

-- GOOD: Use your namespace
MyMudPackage.customEcho = function(msg)
    cecho("<gold>" .. msg)
end
```

**3. Group Related Globals:**
```lua
-- BAD: Multiple globals
playerHealth = 100
playerMana = 50
playerName = "Hero"

-- GOOD: Organized namespace
MyMudPackage.player = {
    health = 100,
    mana = 50,
    name = "Hero"
}
```

### Trigger Optimization 

**Performance Hierarchy:**
1. **Substring triggers** - Fastest for simple patterns
2. **Begin of line substring** - Good for line-start patterns
3. **Perl regex** - Most flexible but slower
4. **Multi-line triggers** - Use sparingly

**Optimization Strategy:**
```lua
-- Use substring gate for complex regex
-- Gate trigger: substring "Health:"
-- Main trigger: regex "^Health: (\d+)/(\d+) Mana: (\d+)/(\d+)$"
```

### User Interface Guidelines

**Responsive Design with Geyser:**
```lua
-- Use percentage-based sizing [[11]]
MyMudPackage.GUI.container = Geyser.Container:new({
    name = "MyMudPackage_Container",
    x = "70%", y = 0,
    width = "30%", height = "100%"
})

-- Create adjustable panels
MyMudPackage.GUI.statsPanel = Adjustable.Container:new({
    name = "MyMudPackage_Stats",
    x = 0, y = 0,
    width = "100%", height = "40%"
}, MyMudPackage.GUI.container)
```

**Asset Management:**
```lua
-- Always use forward slashes for cross-platform compatibility [[11]]
local imagePath = getMudletHomeDir() .. "/MyMudPackage/images/health.png"
local fontPath = getMudletHomeDir() .. "/MyMudPackage/fonts/custom.ttf"

-- Bundle fonts for consistency
setFont("MyMudPackage_Display", fontPath)
```

### Stylesheets are Qt, not CSS {#qt-stylesheets}

Mudlet styles widgets with **Qt Style Sheets (QSS)**, which resemble CSS but are a distinct, smaller language. Since **Mudlet 4.20 all platforms build against Qt6** (Qt 6.9), so styling behaviour shifted for anyone upgrading from an older release.

Practical rules:

-   **Only QSS-supported properties work.** Notably, **`box-shadow` does not exist in QSS** and is silently ignored — as are most modern CSS features (flexbox, grid, transforms, transitions, custom properties). Layout is Geyser's job, not the stylesheet's.
-   Prefer explicit longhand properties (`border-width`, `border-color`, `border-style`) over shorthands where behaviour is ambiguous.
-   `background-image` does not scale; use **`border-image`** when you need the image to stretch to the widget.
-   Qt6 parses stylesheets more strictly than Qt5. A malformed declaration can cause the surrounding rule to be dropped, which typically shows up as a **silently unstyled widget** rather than an error.
-   Verify texture/image paths resolve at runtime — a missing file also yields a silently unstyled widget.

### Label callbacks: prefer closures {#label-callbacks}

The legacy form passes a **function name as a string plus trailing arguments**:

```lua
-- LEGACY: fragile, relies on global lookup + stored argument references
tab:setClickCallback("demonnicChatSwitch", tab)
```

This surface was directly affected by the callback-lifetime and registry-index work in Mudlet 4.20/4.21 (see [#9254](https://github.com/Mudlet/Mudlet/issues/9254)). Prefer a closure, which captures the value lexically and does not depend on a global name:

```lua
-- PREFERRED
tab:setClickCallback(function() demonnicChatSwitch(tab) end)
```

### Resize handling {#resize-handling}

`sysWindowResize` is the traditional signal, but it is **not reliable on all window managers** — see the open upstream bug [#9262](https://github.com/Mudlet/Mudlet/issues/9262), where tiled windows stop emitting it. Mudlet 4.20 added **`sysConsoleSizeChanged`**, which fires on resize and on toggling timestamps; use it as a supplementary signal when layout must track the console size.

## Advanced Features & Integration {#advanced-features}

### GMCP Integration 

**Automatic Package Installation:**
If you control the MUD server, implement GMCP-based auto-installation:

```lua
-- Server sends after login
Client.GUI {
    "version": "2.1.0",
    "url": "https://yourmud.com/packages/latest.mpackage"
}

-- Client-side handler
registerAnonymousEventHandler("gmcp.Client.GUI", function()
    local data = gmcp.Client.GUI
    if data.version > MyMudPackage.version then
        downloadFile(getMudletHomeDir() .. "/update.mpackage", data.url)
        cecho("\n<yellow>Package update available! Restart Mudlet to apply.")
    end
end)
```

**GMCP Event Handling:**
```lua
-- Register for game events
registerAnonymousEventHandler("gmcp.Char.Vitals", function()
    MyMudPackage.updateVitals(gmcp.Char.Vitals)
end)

registerAnonymousEventHandler("gmcp.Room.Info", function()
    if MyMudPackage.settings.autoMap then
        MyMudPackage.Mapper.updateRoom(gmcp.Room.Info)
    end
end)
```

### Package Lifecycle Management 

**`sysLoadEvent` carries a flag since Mudlet 4.20:**

`sysLoadEvent` now passes a boolean — `true` for a fresh profile load, `false` when it fires after `resetProfile()` ([#7726](https://github.com/Mudlet/Mudlet/pull/7726)). Handlers that ignore it still work, but they cannot tell the two cases apart, which matters when the package is already connected and holds live state:

```lua
registerAnonymousEventHandler("sysLoadEvent", function(_, isNewLoad)
    if isNewLoad then
        MyMudPackage.Core.initialize()      -- cold start
    else
        MyMudPackage.Core.reacquireState()  -- after resetProfile(), likely still connected
    end
end)
```

**Installation Hook:**
```lua
registerAnonymousEventHandler("sysInstallPackage", function(event, package)
    if package == "MyMudPackage" then
        cecho("\n<green>Welcome to MyMudPackage v" .. MyMudPackage.version .. "!")
        cecho("\n<yellow>Type 'mypkg help' for commands")
        MyMudPackage.Core.initialize()
        MyMudPackage.showWelcomeScreen()
    end
end)
```

**Uninstallation Cleanup:**
```lua
registerAnonymousEventHandler("sysUninstallPackage", function(event, package)
    if package == "MyMudPackage" then
        -- Hide UI elements
        if MyMudPackage.GUI.container then
            MyMudPackage.GUI.container:hide()
        end
        
        -- Save user preferences
        MyMudPackage.Config.save()
        
        -- Cleanup handlers
        MyMudPackage.Events.unregister()
        
        cecho("\n<yellow>MyMudPackage uninstalled. Settings preserved.")
    end
end)
```

### Error Handling & Debugging

```lua
-- Wrap critical functions in error handlers
function MyMudPackage.safeExecute(func, ...)
    local success, result = pcall(func, ...)
    if not success then
        MyMudPackage.logError(result)
        cecho("\n<red>Error in MyMudPackage: Check debug console")
    end
    return success, result
end

-- Comprehensive logging
function MyMudPackage.log(level, message)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    local logEntry = string.format("[%s] %s: %s", timestamp, level, message)
    
    -- Console output for debugging
    if MyMudPackage.settings.debugMode then
        echo("\n[MyMudPackage] " .. logEntry)
    end
    
    -- File logging
    local logFile = getMudletHomeDir() .. "/MyMudPackage.log"
    local file = io.open(logFile, "a")
    if file then
        file:write(logEntry .. "\n")
        file:close()
    end
end
```

## Distribution & Maintenance {#distribution}

### Package Repository Submission 

Submit to the official **Mudlet Package Repository** for maximum visibility:

1. **Web Upload**: Visit [packages.mudlet.org/upload](https://packages.mudlet.org/upload) 
2. **GitHub PR**: Fork [mudlet-package-repository](https://github.com/Mudlet/mudlet-package-repository) 

**Repository Requirements:**
- Comprehensive documentation
- Clear versioning
- Proper dependency declarations
- Tested on multiple platforms Version Management 

Follow **Semantic Versioning**:
- **Major (X.0.0)**: Breaking changes
- **Minor (1.X.0)**: New features, backward compatible
- **Patch (1.2.X)**: Bug fixes only

```lua
-- Version checking system
MyMudPackage.checkForUpdates = function()
    local current = MyMudPackage.version
    local latest = mpkg.getRepositoryVersion("MyMudPackage")
    
    if compareVersions(latest, current) > 0 then
        cecho(string.format("\n<yellow>Update available: %s -> %s", current, latest))
        cecho("\n<green>Use: mpkg upgrade MyMudPackage")
    end
end
```

### Documentation Excellence

**In-Package Help System:**
```lua
MyMudPackage.help = {
    topics = {
        main = {
            title = "MyMudPackage Help",
            content = [[
Commands:
  mypkg help <topic>  - Get detailed help
  mypkg config        - Open configuration
  mypkg status        - Show current status
  
Topics: setup, combat, mapping, troubleshooting
            ]]
        },
        setup = {
            title = "Initial Setup",
            content = [[
1. Configure your character name: mypkg set name <yourname>
2. Set your class: mypkg set class <warrior|mage|rogue>
3. Enable features: mypkg enable <feature>
            ]]
        }
    },
    
    show = function(topic)
        topic = topic or "main"
        local help = MyMudPackage.help.topics[topic]
        if help then
            cecho("\n<cyan>═══ " .. help.title .. " ═══\n")
            cecho(help.content)
        else
            cecho("\n<red>Unknown topic. Available: " .. 
                  table.concat(table.keys(MyMudPackage.help.topics), ", "))
        end
    end
}
```

## Professional Workflow & Tools {#professional-workflow}

### Development Environment Setup

**1. IDE Configuration:**
- Install VS Code with Lua extensions
- Configure [EmmyLua](https://github.com/EmmyLua) for autocomplete
- Set up Mudlet API definitions

**2. Version Control (.gitignore):**
```gitignore
# Build outputs
build/
*.mpackage

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
```

### Continuous Integration 

**GitHub Actions Workflow:**
```yaml
name: Build Mudlet Package

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build with Muddler
      uses: demonnic/build-with-muddler@main
      with:
        muddlerVersion: 2.0.1
    
    - name: Upload Package
      uses: actions/upload-artifact@v3
      with:
        name: MyMudPackage
        path: build/tmp/*.mpackage
```

### Quality Assurance Checklist

Run the automated validation commands from the project workflow first. Then use
a supported Mudlet release for this hands-on smoke test:

- Freshly import the complete package and confirm bundled images and audio
  resolve from the installed asset paths.
- Connect, reconnect, and run `resetProfile()` without losing the mapper,
  MSDP subscriptions, or visible GUI state.
- Exercise player/group/affect data, resource and opponent gauges, action
  icons, room information, and both ASCII and Mudlet map modes.
- Exercise YATCO startup, tab switching, captured chat, and sound toggles.
- Exercise package aliases and numeric-keypad movement bindings, including
  modifier keys.
- Run `fix gui` repeatedly and confirm there is no duplicated output,
  handler growth, or progressively slower refresh.
- Save and reload Adjustable.Container profiles; resize the window and
  confirm parenting, visibility, and z-order remain correct.
- Test the supported in-place upgrade path. Consult
  [MUDLET_COMPATIBILITY.md](MUDLET_COMPATIBILITY.md) before attributing a
  package-removal crash or resize failure to LuminariGUI.

### Performance Monitoring

```lua
-- Performance profiling utilities
MyMudPackage.Profiler = {
    timers = {},
    
    start = function(name)
        MyMudPackage.Profiler.timers[name] = getTimestamp()
    end,
    
    stop = function(name)
        local start = MyMudPackage.Profiler.timers[name]
        if start then
            local elapsed = getTimestamp() - start
            MyMudPackage.log("PROFILE", string.format("%s took %.3fms", name, elapsed))
            MyMudPackage.Profiler.timers[name] = nil
        end
    end
}

-- Usage example
MyMudPackage.Profiler.start("complexOperation")
-- ... your code ...
MyMudPackage.Profiler.stop("complexOperation")
```

## Conclusion

Creating exceptional Mudlet packages requires careful planning, adherence to best practices, and attention to user experience. This guide provides the foundation for developing professional-quality packages that enhance gameplay and showcase your MUD's unique features.

**Key Success Factors:**
- **Clear Architecture**: Modular, maintainable code structure
- **Performance**: Optimized triggers and efficient scripting
- **User Experience**: Intuitive interfaces and comprehensive documentation
- **Reliability**: Robust error handling and thorough testing
- **Community**: Active maintenance and responsive support

By following these guidelines and leveraging Mudlet's powerful features you can create packages that significantly enhance the gaming experience for your MUD's players while maintaining professional standards of quality and usability.
