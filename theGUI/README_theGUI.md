# LuminariGUI Source-to-Build System

This directory contains the source-to-build system for assembling `LuminariGUI.xml` from modular source fragments, plus the package manager for creating distributable `.mpackage` files.

## Overview

Mudlet requires a single XML package file, but development and maintenance benefit from modular source files. This build system:

1. **Extracts** the monolithic `LuminariGUI.xml` into manageable source fragments
2. **Assembles** source fragments back into the final `LuminariGUI.xml`
3. **Validates** both fragments and final output
4. **Packages** the XML into distributable `.mpackage` files with full release workflow

## Directory Structure

```
theGUI/
├── build.py          # Build/extract script
├── package.py        # Package manager and release workflow
├── build.yaml        # Build manifest (fragment list, version)
├── skeleton.xml      # Package structure template
├── README.md         # This file
└── src/              # Source fragments
    ├── triggers/     # Trigger definitions
    ├── aliases/      # Alias definitions
    ├── scripts/      # Script definitions
    └── keys/         # Key binding definitions
```

## Quick Start

### First-Time Setup (Extract existing XML)

```bash
cd theGUI
python build.py --extract
```

This creates source fragments from the existing `LuminariGUI.xml`.

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
| `python build.py --extract` | Split existing XML into fragments |
| `python build.py --diff` | Show what would change |
| `python build.py --stats` | Show line counts and statistics |
| `python build.py --clean` | Remove generated output file |
| `python build.py --watch` | Watch files and rebuild on changes |

## Package Manager (package.py)

After building the XML, use `package.py` to create distributable `.mpackage` files.

### Commands

| Command | Description |
|---------|-------------|
| `python package.py create` | Create release package (runs build & tests) |
| `python package.py create --dev` | Create dev package with timestamp |
| `python package.py create --skip-build` | Package existing XML without rebuilding |
| `python package.py release` | Full release workflow (build, test, branch, tag) |
| `python package.py release --dry-run` | Preview release without changes |
| `python package.py release --push` | Release and push to remote |
| `python package.py list` | List existing packages |
| `python package.py clean` | Remove old dev packages |

### Quick Examples

```bash
# Build XML and create package for testing
python build.py && python package.py create --dev

# Full release
python package.py release --push
```

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
  - src/scripts/00_msdpmapper.xml
  - src/scripts/01_gui.xml
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
5. Commit both source and output

### Adding New Functionality

1. Create a new fragment file (e.g., `src/scripts/04_new_feature.xml`)
2. Add it to `build.yaml` in the appropriate section
3. Build and test

### Watch Mode

For active development:
```bash
python build.py --watch
```
Automatically rebuilds when source files change.

## Fragment Format

Each fragment must be valid XML that can be injected into the skeleton structure.

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
- Both source and output (`LuminariGUI.xml`) are tracked in git
- Users can download `LuminariGUI.xml` directly without building

## Troubleshooting

### Validation Errors

```
ERROR: Malformed XML in src/scripts/01_gui.xml
  Line 45: Unclosed tag <Script>
```

Check the fragment file for XML syntax errors.

### Build Differences

Use `python build.py --diff` to see what would change.

### Missing Fragments

```
WARNING: Fragment not found: src/scripts/missing.xml
```

Either create the file or remove it from `build.yaml`.

## Dependencies

- Python 3.8+
- Optional: PyYAML (`pip install pyyaml`) for faster config parsing
