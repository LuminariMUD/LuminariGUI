# AGENTS.md — repository guidance for coding agents

This is the canonical agent-instruction file. `CLAUDE.md` and `GEMINI.md` are
relative symlinks to this file; edit `AGENTS.md` and preserve those symlinks.

## Project Overview

LuminariGUI is a Mudlet GUI package for LuminariMUD providing real-time MSDP integration, tabbed chat (YATCO), interactive mapping, and status monitoring. The codebase uses embedded Lua scripts within XML files using Mudlet's package format.

**Mudlet compatibility:** The current documented release is Mudlet 4.22.0.
Mudlet 4.20 migrated to Qt6, while 4.21 changed label/callback internals and
MSDP negotiation. Before diagnosing "the GUI is broken," read
`docs/MUDLET_COMPATIBILITY.md` — it covers 4.19 through 4.22, distinguishes
upstream Mudlet regressions from package bugs, and lists known issues in this
codebase.

## Build Commands

Run all commands from the repository root unless noted.

```bash
# Build the package (auto-increments version, archives old version)
python3 theGUI/build.py

# Validate without making changes
python3 theGUI/build.py --validate

# DESTRUCTIVE: overwrite source fragments and build.yaml from the built XML
python3 theGUI/build.py --extract

# MUTATING: build immediately, then rebuild/version-bump on every change
python3 theGUI/build.py --watch

# Show what would change
python3 theGUI/build.py --diff

# Show build statistics
python3 theGUI/build.py --stats

# DESTRUCTIVE: delete the generated LuminariGUI.xml
python3 theGUI/build.py --clean

# Exit non-zero if output would change (CI guard)
python3 theGUI/build.py --diff --fail-on-diff

# Build an exact version instead of auto-incrementing
python3 theGUI/build.py --version 2.0.4.029
```

`--validate`, `--diff`, `--stats`, and `--diff --fail-on-diff` are read-only.
A normal build updates `theGUI/build.yaml`, archives the previous XML, and
rewrites `LuminariGUI.xml`. Avoid `--extract`, `--watch`, or `--clean` unless
that mutation is specifically intended.

## Package Commands

```bash
# Create a local distributable package only (builds XML, runs tests)
python3 theGUI/package.py create

# Create dev package with timestamp
python3 theGUI/package.py create --dev

# Publish a complete release (including GitHub page and uploaded assets)
python3 theGUI/package.py release

# Preview the publishing workflow without changes
python3 theGUI/package.py release --dry-run

# List existing packages
python3 theGUI/package.py list

# DESTRUCTIVE: delete old dev packages (keeps 3 by default)
python3 theGUI/package.py clean --keep 3
```

`create` and `release` both accept `--version <ver>` to build and package that
exact version consistently across `build.yaml`, the XML, package metadata,
release branch, and tag. With `--skip-build`, the requested/current version
must already match the version embedded in `LuminariGUI.xml`; packaging refuses
a mismatch. Both commands accept `--skip-build` / `--skip-tests`, and `release`
also accepts `--skip-git-check`.

**A release is never local-only.** `package.py release` atomically pushes
`master`, `release/v<version>`, and `v<version>` to `origin`, verifies all three
remote refs, publishes the GitHub Release page through authenticated `gh`, and
attaches and verifies both the `.mpackage` and JSON metadata. There is no
commit-without-push release mode. Use `create` when the requested outcome is
only a local `.mpackage`.

Do not report a release complete unless the command reaches its final
`fully published and verified` status. Independently confirm with
`git ls-remote` and `gh release view` before handing the result back to the
user.

`package.py` invokes the test suite itself, so `create` and `release` run tests
without requiring a separate working-directory setup.

## Testing Commands

The runner and standalone Python suites resolve their default XML relative to
the repository, so they work from either the repository root or `tests/`.

```bash
# Run all test suites supported by the installed external tools
python3 tests/run_tests.py --skip-optional

# Equivalent from tests/
cd tests && python3 run_tests.py --skip-optional
```

**`--skip-optional` matters.** If `luacheck` or another external test tool is
missing and you omit the flag, the runner prints "Missing dependencies" and
**exits 1 before running any suites**. Pass `--skip-optional` to run every
suite supported by the installed tools, or install the missing tools to run
the complete set.

```bash
# Validate XML and Lua syntax (works from repo root, no XML arg needed)
python3 scripts/validate_package.py

# Run one suite via the runner
python3 tests/run_tests.py --skip-optional --test syntax
#   valid: syntax, quality, functions, events, lifecycle, system, performance

# Or invoke a suite directly
python3 tests/test_lua_syntax.py
```

Other runner flags: `--parallel` / `--sequential`, `--report <file>`,
`--format text|json`, `--verbose` (adds runner configuration), and `--quiet`
(suppresses suite output and prints one final status line).

### Other scripts

```bash
python3 scripts/format_xml.py       # XML formatting
python3 scripts/analyze_handlers.py # Event handler analysis
```

There is no `requirements.txt` and no required third-party Python package.
`build.py` uses PyYAML when available and otherwise uses its built-in parser.
External tools `lua`/`luac` (and optionally `luacheck`) enable the Lua test
suites.

## Architecture

### Source-to-Build System

**Edit source files in `theGUI/src/`, NOT `LuminariGUI.xml` directly.**

```
theGUI/
├── build.py          # Build script (XML assembly)
├── package.py        # Package manager (mpackage creation, releases)
├── build.yaml        # Manifest (fragment list, version)
├── skeleton.xml      # Package structure template
└── src/              # SOURCE OF TRUTH
    ├── triggers/     # Trigger definitions
    ├── aliases/      # Alias definitions
    ├── scripts/      # Lua scripts and composite wrappers
    │   └── gui/      # Focused children included by 01_gui.xml
    └── keys/         # Key bindings
```

The build system assembles `theGUI/src/` fragments into `LuminariGUI.xml`. Each build:
1. Auto-increments version in `build.yaml`
2. Archives previous `LuminariGUI.xml` to `docs/archive/`
3. Assembles new package

### Key Components (in `theGUI/src/scripts/`)

- **MSDPMapper** (`00_msdpmapper.xml`): MSDP protocol handling and room mapping
- **GUI wrapper** (`01_gui.xml`): Outer/nested Mudlet group scaffolding and the
  explicit ordered include index for `scripts/gui/`
- **GUI children** (`scripts/gui/*.xml`): Focused widgets, MSDP updates,
  initialization, event ownership, refresh, and lifecycle scripts; no child is
  intended to exceed roughly 300 Lua lines
- **YATCOConfig** (`02_yatcoconfig.xml`): Chat system configuration
- **YATCO** (`03_yatco.xml`): Tabbed chat organization

Other fragments: `triggers/` (`00_yatcoconfig.xml`, `01_gui.xml`), `aliases/` (`00_toggles.xml`, `01_yatco.xml`), `keys/` (`00_movement.xml`). The full assembly order is defined in `theGUI/build.yaml`.

### Fragment File Naming

```
NN_descriptive_name.xml

NN = 00-09 for core/init, 10-19 for major subsystems, 20+ for extensions
```

## Code Conventions

### Lua Namespacing

```lua
-- Use GUI. prefix for GUI functions/variables
GUI.Health = Geyser.Gauge:new({...})
function GUI.updateHealthGauge() ... end

-- Safe table initialization
GUI.AffectIcons = GUI.AffectIcons or {}

-- Always provide fallbacks for MSDP data
local health = tonumber(msdp.HEALTH) or 0
```

### Event Registration

Most handlers are **not** registered with scattered direct calls.
`GUI.registerEventHandlers()` in `scripts/gui/51_event_registry.xml` holds the
central `GUI.EVENT_HANDLERS` table. The shared ownership functions in
`src/scripts/00_resources.xml` replace prior IDs and log registration errors.
**Add new MSDP-driven handlers to that table**, not as standalone calls:

```lua
GUI.EVENT_HANDLERS = {
    ["msdp.HEALTH"]        = "GUI.updateHealthGauge",
    ["msdp.HEALTH_MAX"]    = "GUI.updateHealthGauge",
    ["msdp.MOVEMENT"]      = "GUI.updateMovesGauge",
    ["msdp.MOVEMENT_MAX"]  = "GUI.updateMovesGauge",
    -- ...
}
```

**`GUI.registerEventHandlers()` is called on every `GUI.init()` and every `GUI.initializeOrRefresh()`, so it must stay idempotent.** It kills only the table entries for events owned by `GUI.EVENT_HANDLERS` before re-registering. Do not sweep every ID in `GUI.eventHandlerIds`: older installations retain IDs for the file-scope mapper/protocol handlers, and Mudlet 4.21 can reuse those IDs during an in-place upgrade. Without cleanup of the owned entries, handlers stack on every refresh — this was a real bug (36 → 324 live handlers over ten refreshes). If you add an owned registration path, record its ID there too.

**Do not add an event to the table if it is already registered at file scope** — Mudlet allows multiple handlers per event, so duplicates silently double the work. `map.eventHandler` and `map.onProtocolEnabled` are registered at file scope in `00_msdpmapper.xml` (`msdp.ROOM`, `shiftRoom`, `sysConnectionEvent`, `sysDownloadDone`, `sysProtocolEnabled`) and must **not** be repeated in the GUI tables. Note `msdp.ROOM` legitimately has two *different* handlers: `GUI.updateRoom` (table) and `map.eventHandler` (file scope).

Lifecycle events are registered at file scope, but
`scripts/gui/53_lifecycle.xml` owns all six IDs in
`GUI.lifecycleHandlerIds` and replaces them through its
`registerLifecycleHandler()` helper. Do not add an untracked lifecycle
registration: Mudlet can retain function-reference handlers across an
in-session package replacement, which otherwise duplicates load/connection
work. `sysExitEvent` and `sysUninstallPackage` also belong in this registry.

All runtime timers use stable names through `GUI.setOwnedTimer()`. Do not add
raw `tempTimer()` calls. One-shot callbacks remove their ID before invoking
application code, recurring callbacks replace their previous ID, and package
uninstall cancels the complete `GUI.ownedTimerIds` registry. Run
`python3 scripts/analyze_handlers.py --fail-on-unowned` after changing handler
or timer ownership. The full contract and current exact counts are documented
in `docs/RESOURCE_LIFECYCLE.md`.

Since Mudlet 4.20, `sysLoadEvent` passes a boolean second argument (`true` = fresh load, `false` = after `resetProfile()`). The package uses this: after a reset, neither `sysConnectionEvent` nor `sysProtocolEnabled` fires again, so it calls `map.initialize()` to recreate both map views, then `GUI.requestMSDPReports()` and `GUI.initializeOrRefresh()`.
Mudlet also clears the global `msdp` table during a reset, so the refresh path
must recreate it before reading any fields.

MSDP subscriptions live in `GUI.MSDP_REPORT_VARS` in
`scripts/gui/40_msdp_protocol.xml`; add new variables there rather than writing
bare `sendMSDP("REPORT", ...)` calls.

### CSS Styling (CSSMan)

```lua
GUI.BoxCSS = CSSMan.new([[
  background-image: url(]] .. getMudletHomeDir():gsub("\\", "/") ..
  [[/LuminariGUI/images/ui_texture.png);
]])
component:setStyleSheet(GUI.BoxCSS:getCSS())
```

These are **Qt Style Sheets (QSS)**, not CSS. Unsupported properties are silently ignored — `box-shadow` in particular does not exist in QSS. Use `border-image` (not `background-image`) when an image must stretch to the widget. See `docs/MUDLET_COMPATIBILITY.md` for Qt6 specifics.

### Path Handling

Always use forward slashes for cross-platform compatibility:
```lua
local path = getMudletHomeDir():gsub("\\", "/") .. "/LuminariGUI/images/"
```

## Development Workflow

1. Edit source fragments in `theGUI/src/`
2. Validate: `python3 theGUI/build.py --validate`
3. Build: `python3 theGUI/build.py`
4. Test: `cd tests && python3 run_tests.py --skip-optional` (see the caveat in Testing Commands)
5. Validate the built package: `python3 scripts/validate_package.py`
6. Import `LuminariGUI.xml` into Mudlet for manual testing
7. Review `git status`, then commit the changed source fragments,
   `theGUI/build.yaml`, `LuminariGUI.xml`, and any newly generated tracked
   archive file.

Note that step 3 auto-increments the version in `build.yaml` on every build, so avoid rebuilding gratuitously.

## XML Structure

Source fragments must be valid XML that inject into the skeleton:

```xml
<ScriptGroup isActive="yes" isFolder="yes">
    <name>FeatureName</name>
    <packageName></packageName>
    <script></script>
    <eventHandlerList />
    <Script isActive="yes" isFolder="no">
        <name>ScriptName</name>
        <packageName></packageName>
        <script>-- Lua code here</script>
        <eventHandlerList />
    </Script>
</ScriptGroup>
```

Mudlet expects `<packageName>`, `<script>`, and `<eventHandlerList>` on both the group and the script elements — omitting them produces XML that validates but may not import cleanly. Match the structure of the existing fragments.

Remember to escape XML special characters: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`
