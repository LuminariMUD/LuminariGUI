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
*   **[Python Tools](docs/PYTHON_TOOLS.md)**: Guide to the automated build and testing tools (`validate_package.py`, `run_tests.py`, etc.).
*   **[Protocol Reference](docs/PROTOCOL_REFERENCE.md)**: Details on MSDP variables and how they map to the GUI.
*   **[Sound Usage](docs/SOUND_USAGE.md)**: Configuration for sound triggers and audio assets.
*   **[Changelog](docs/CHANGELOG.md)**: History of changes and updates.

## Development

This project uses a single-file XML structure (`LuminariGUI.xml`) managed with Python automation tools.

*   **Validation**: Run `python3 scripts/validate_package.py` to check for errors.
*   **Testing**: Run `python3 run_tests.py` to execute the test suite.

See [MUDLET_DEVELOPMENT.md](docs/MUDLET_DEVELOPMENT.md) for more details.

## License

This project is released into the public domain under the [The Unlicense](LICENSE).

