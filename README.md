# LuminariGUI

LuminariGUI is a comprehensive graphical user interface package for [LuminariMUD](http://luminarimud.com/), built for the [Mudlet](https://www.mudlet.org/) client. It provides real-time data integration, advanced mapping, and a customizable chat interface to enhance the gameplay experience.

## Features

*   **Real-time Status Monitoring**: Instant updates on health, movement, mana, and other vital statistics via MSDP (MUD Server Data Protocol).
*   **Interactive Mapping**: Automatic room mapping and navigation assistance using `MSDPMapper`.
*   **Tabbed Chat System**: Organized chat channels using the YATCO (Yet Another Tabbed Chat Organization) framework.
*   **Spell Casting Console**: Visual tracking of spell casting progress.
*   **Group Management**: Live status display of group members.
*   **Affects Tracking**: Visual indicators for active spells and status effects.
*   **Customizable Layout**: Geyser-based UI components with CSS styling.

## Installation

> **Mudlet version:** Mudlet 4.20 migrated to Qt6 and 4.21 changed label/callback internals and MSDP negotiation. If you have recently upgraded Mudlet and the GUI is misbehaving, see **[Mudlet Compatibility](docs/MUDLET_COMPATIBILITY.md)** — it includes a triage checklist. The most common cause is that **MSDP needs re-enabling**: since 4.20 the protocol settings live in a *dropdown* under Profile Preferences → Protocols, not the old checkbox list.

> **Diagnostic build:** Screen diagnostics are controlled by the single
> `GUI.DEBUG` switch in `theGUI/src/scripts/00_debug.xml`. See
> **[Screen Diagnostics](docs/DEBUGGING.md)** for output prefixes and report
> collection.

1.  **Download**: Get the latest `LuminariGUI.xml` file from the [Releases](Releases/) folder or the latest release tag.
2.  **Import into Mudlet**:
    *   Open Mudlet and connect to your profile.
    *   Drag and drop the `LuminariGUI.xml` file into the main Mudlet window.
    *   *Alternatively*: Go to **Toolbox** -> **Package Manager** -> **Install** and select the file.
3.  **Restart**: It is recommended to restart Mudlet after installing to ensure all scripts and assets initialize command.

## Quick Start

Once installed, the GUI should automatically load when you connect to LuminariMUD.

*   **Chat**: Chat windows will appear in tabs. You can configure chat gagging and other settings.
*   **Map**: The mapper should start tracking your movement automatically.
*   **Status**: Gauges and info boxes will update as you play.

## Documentation

Detailed documentation is available in the `docs/` directory:

*   **[Developer Guide](docs/MUDLET_DEVELOPMENT.md)**: Architecture, best practices, and workflow for contributing to the project.
*   **[Mudlet Compatibility](docs/MUDLET_COMPATIBILITY.md)**: What changed in Mudlet 4.20–4.22, known upstream bugs, and a "the GUI broke after updating" triage checklist.
*   **[Build System Guide](theGUI/README_theGUI.md)**: How to use the source-to-build system for modular XML development.
*   **[Python Tools](docs/PYTHON_TOOLS.md)**: Guide to the automated build and testing tools (`validate_package.py`, `run_tests.py`, etc.).
*   **[Protocol Reference](docs/PROTOCOL_REFERENCE.md)**: Details on MSDP variables and how they map to the GUI.
*   **[Sound Usage](docs/SOUND_USAGE.md)**: Configuration for sound triggers and audio assets.
*   **[Changelog](docs/CHANGELOG.md)**: History of changes and updates.
*   **[Historical Changelog](docs/HISTORICAL_CHANGELOG.md)**: Preserved release history through v2.0.4.016.
*   **[Project Task List](docs/ongoing-projects/TASK_LIST.md)**: The single tracker for unfinished work.
*   **[Contributing](CONTRIBUTING.md)**: Guidelines for contributing to the project.

## Development

This project uses a modular source-to-build system (`theGUI/`) that assembles XML fragments into the final `LuminariGUI.xml` package. Each build automatically increments the version and archives the previous release.

*   **Build**: Run `python3 theGUI/build.py` to assemble the XML package.
*   **Package**: Run `python3 theGUI/package.py create` to create a local distributable `.mpackage`.
*   **Release**: Run `python3 theGUI/package.py release` to build, commit, tag, merge, atomically publish and verify all release refs, and create the GitHub Release with the `.mpackage` and JSON metadata attached. A release never stops at local commits.
*   **Testing**: Run `python3 tests/run_tests.py` to execute the test suite.
*   **Validation**: Run `python3 scripts/validate_package.py` to check for errors.

See [theGUI/README_theGUI.md](theGUI/README_theGUI.md) for build system details and [MUDLET_DEVELOPMENT.md](docs/MUDLET_DEVELOPMENT.md) for architecture and workflow.

## License

This project is released into the public domain under the [The Unlicense](LICENSE).
