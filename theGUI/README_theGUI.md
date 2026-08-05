# LuminariGUI Source-to-Build System

This directory contains the source-to-build system for assembling `LuminariGUI.xml` from modular source fragments, plus the package manager for creating distributable `.mpackage` files.

## Overview

Mudlet requires a single XML package file, but development and maintenance benefit from modular source files. This build system:

1. **Assembles** source fragments into the final `LuminariGUI.xml`
2. **Expands** explicit composite-fragment includes without flattening Mudlet groups
3. **Validates** physical fragments, expanded fragments, and final output
4. **Packages** the XML into distributable `.mpackage` files with full release workflow

## Directory Structure

```
theGUI/
├── build.py          # Build/extract script
├── package.py        # Package manager and release workflow
├── build.yaml        # Build manifest (fragment list, version)
├── skeleton.xml      # Package structure template
├── README_theGUI.md  # This file
└── src/              # Source fragments
    ├── triggers/     # Trigger definitions
    ├── aliases/      # Alias definitions
    ├── scripts/      # Script definitions and composite wrappers
    │   └── gui/      # Focused children of the composite GUI wrapper
    └── keys/         # Key binding definitions
```

## Quick Start

### First-Time Setup (Extract existing XML)

```bash
cd theGUI
python build.py --extract
```

This overwrites source fragments and regenerates `build.yaml` from the existing
`LuminariGUI.xml`; use it only for intentional reverse extraction. The command
refuses before writing while a configured fragment contains `BUILD_INCLUDE`,
because reverse extraction cannot preserve a composite layout safely.

### Build Package

```bash
python build.py
```

Assembles source fragments into `../LuminariGUI.xml`.

### Validate Only

```bash
python build.py --validate
```

Validates all fragments and the assembly without writing output.

## Commands

| Command | Description |
|---------|-------------|
| `python build.py` | Build the package |
| `python build.py --validate` | Validate only, don't write |
| `python build.py --extract` | **Destructive:** overwrite fragments from existing XML |
| `python build.py --diff` | Show what would change |
| `python build.py --stats` | Show line counts and statistics |
| `python build.py --clean` | **Destructive:** remove generated output file |
| `python build.py --watch` | **Mutating:** build immediately and on each change |
| `python build.py --version VERSION` | Build one exact version without incrementing |

## Package Manager (package.py)

After building the XML, use `package.py` to create distributable `.mpackage` files.

### Commands

| Command | Description |
|---------|-------------|
| `python package.py create` | Create a local distributable package (runs build & tests) |
| `python package.py create --dev` | Create dev package with timestamp |
| `python package.py create --skip-build` | Package existing XML without rebuilding |
| `python package.py create --version VERSION` | Build and package one exact version |
| `python package.py release` | Publish and verify refs, GitHub Release, and both assets |
| `python package.py release --version VERSION` | Build and publish one exact version |
| `python package.py release --dry-run` | Preview publication without changes |
| `python package.py list` | List existing packages |
| `python package.py clean` | **Destructive:** remove old dev packages |

### Quick Examples

```bash
# Build XML and create package for testing
python build.py && python package.py create --dev

# Publish the complete release
python package.py release
```

`release` has no local-only completion mode: it verifies that `master`, the
release branch, and the tag reached `origin`, creates the GitHub Release page,
uploads the `.mpackage` and JSON metadata, and verifies both assets. Use
`create` when only a local artifact is wanted. See
[`docs/PYTHON_TOOLS.md`](../docs/PYTHON_TOOLS.md).

## Configuration (build.yaml)

```yaml
package:
  name: "LuminariGUI"
  version: "2.0.4.015"

output:
  file: "../LuminariGUI.xml"
  encoding: "UTF-8"

options:
  embed_markers: false      # Add source file comments in output
  validate_fragments: true  # Validate each fragment's XML
  validate_output: true     # Validate final assembled XML

triggers:
  - src/triggers/00_yatcoconfig.xml
  - src/triggers/01_gui.xml

aliases:
  - src/aliases/00_toggles.xml
  - src/aliases/01_yatco.xml

scripts:
  - src/scripts/00_debug.xml
  - src/scripts/00_adjustablecontainers.xml
  - src/scripts/00_msdpmapper.xml
  - src/scripts/01_gui.xml  # Composite wrapper; children are ordered inside it
  # ... more fragments

keys:
  - src/keys/00_movement.xml
```

## Development Workflow

### Making Changes

1. Edit the appropriate source fragment in `src/`
2. Validate: `python build.py --validate`
3. Build: `python build.py`
4. Test in Mudlet
5. Commit source, `build.yaml`, output, and any new tracked archive

### Adding New Functionality

1. Create a new fragment file (e.g., `src/scripts/04_new_feature.xml`)
2. Add it to `build.yaml` in the appropriate section
3. Build and test

### Watch Mode

For active development:
```bash
python build.py --watch
```
Runs a build immediately, then rebuilds and version-bumps when source files
change.

## Fragment Format

Each fragment must be valid XML that can be injected into the skeleton structure.

### Composite Script Fragments

`src/scripts/01_gui.xml` preserves the outer and nested Mudlet `ScriptGroup`
topology while including focused children from `src/scripts/gui/` in explicit
load order:

```xml
<!-- BUILD_INCLUDE: gui/40_msdp_protocol.xml -->
<!-- BUILD_INCLUDE: gui/41_msdp_gauges.xml -->
```

Include paths are relative to the file containing the directive. They must be
explicit paths: missing files, globs, cycles, and paths outside `theGUI/src`
are fatal. Every physical child and fully expanded wrapper is validated, and
the build directives are removed from `LuminariGUI.xml`. `--stats` lists each
included file separately. Nested XML files are watched by `--watch`.

The inner GUI scripts are intentionally ordered. Protocol definitions precede
their lifecycle registration, component constructors precede `GUI Boot`, and
the event registry and refresh functions precede `GUI Lifecycle`. Add or move
GUI children by editing the wrapper's include list, not `build.yaml`.

#### Duplicate-name validation

Mudlet stores folders and leaf items from one editor section in the same unit
and permits multiple items to share a name. Name-based APIs act on every exact
match, so repeated names in different groups are sometimes intentional. The
build therefore applies a narrower ambiguity rule:

- a folder and leaf share one family (`TriggerGroup`/`Trigger`,
  `AliasGroup`/`Alias`, `ScriptGroup`/`Script`, `TimerGroup`/`Timer`,
  `KeyGroup`/`Key`, or `ActionGroup`/`Action`);
- two direct children of the same parent cannot have the same exact,
  case-sensitive name within that family;
- the same exact name remains valid under different parent groups or in
  different package sections; and
- a group may intentionally share its name with one of its own descendants,
  as `MSDPMapper` and the nested `GUI` groups currently do.

This catches indistinguishable sibling collisions without rejecting the
hierarchy that Mudlet 4.22 explicitly supports. `build.py --validate`, normal
builds, and the generated-output drift check all apply the rule.

#### GUI child responsibilities

The numbered child ranges are stable ownership boundaries:

| Range | Responsibility |
|---|---|
| `00`–`01` | CSSMan and persisted GUI preferences |
| `10`–`12` | Background, borders, and base containers |
| `20`–`22` | Gauges, cast console, and header/action widgets |
| `30`–`36` | Tab shell, affects, group/player data, map controls, room information, and frames |
| `40`–`42` | MSDP subscriptions, gauges/opponent updates, and action-state updates |
| `50`–`53` | File-scope boot, owned event registry, refresh orchestration, and lifecycle handlers |
| `60` | Adjustable-container profiles and persistence |
| `70`–`71` | Scrollbar styling and prompt-line utility |

Preserve these ordering and ownership invariants when adding or moving a child:

- `00_debug.xml` loads first, followed by the AdjustableContainers foundation;
  the mapper and GUI may create containers only after that foundation exists.
- GUI constructors load before the file-scope boot sequence invokes them, and
  the GUI shell exists before YATCO initializes.
- `GUI.registerEventHandlers()` is idempotent and replaces only the event IDs
  owned by its local registration table. It must not sweep file-scope mapper
  or protocol IDs retained during an in-place package upgrade.
- Mapper registrations for `msdp.ROOM`, `shiftRoom`, `sysConnectionEvent`,
  `sysDownloadDone`, and `sysProtocolEnabled` remain file-scope in
  `00_msdpmapper.xml`; do not duplicate them in the GUI registry.
- `msdp.ROOM` intentionally has two different consumers:
  `GUI.updateRoom` updates the room display while `map.eventHandler` updates
  mapping state.
- The map triggers currently invoke `onMapLine()` and `onRoomMapLine()` through
  Mudlet code strings, so those callbacks must remain globally resolvable
  unless the trigger registration is refactored to pass functions directly.
- The immediate boot block remains file-scope. Lifecycle registrations own and
  replace their IDs through `GUI.lifecycleHandlerIds`.

### Script Fragment Example

```xml
<ScriptGroup isActive="yes" isFolder="yes">
    <name>MyFeature</name>
    <packageName></packageName>
    <script></script>
    <eventHandlerList />
    <Script isActive="yes" isFolder="no">
        <name>MyScript</name>
        <packageName></packageName>
        <script>-- Lua code here
function myFunction()
    -- implementation
end
</script>
        <eventHandlerList />
    </Script>
</ScriptGroup>
```

### Trigger Fragment Example

```xml
<TriggerGroup isActive="yes" isFolder="yes">
    <name>MyTriggers</name>
    <!-- trigger properties -->
    <Trigger isActive="yes">
        <name>MyTrigger</name>
        <script>-- trigger script</script>
        <!-- more properties -->
    </Trigger>
</TriggerGroup>
```

## File Naming Convention

```
NN_descriptive_name.xml

NN = Two-digit ordering number (00-99)
     00-09: Core/initialization
     10-19: Major subsystems
     20-29: Secondary systems
     30+:   Extensions/utilities

descriptive_name = lowercase_with_underscores
```

## Version Control

- Source fragments (`src/`) are the source of truth
- Source, `build.yaml`, output (`LuminariGUI.xml`), and generated archives are
  tracked in git
- Users can download `LuminariGUI.xml` directly without building

## Troubleshooting

### Validation Errors

```
ERROR: Invalid source fragment src/scripts/gui/31_affects.xml
  Line 45: Unclosed tag <Script>
```

Check the fragment file for XML syntax errors.

### Build Differences

Use `python build.py --diff` to see what would change.

### Missing Fragments

```
ERROR: Fragment not found: src/scripts/missing.xml
```

Either create the file or remove it from `build.yaml`.

## Dependencies

- Python 3.8+
- Optional: PyYAML (`pip install pyyaml`) for faster config parsing
