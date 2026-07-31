# Contributing to LuminariGUI

Thank you for your interest in contributing!

## Development Guide
Please read [docs/MUDLET_DEVELOPMENT.md](docs/MUDLET_DEVELOPMENT.md) for:
- Project Architecture (source-to-build fragment system)
- Development Workflow
- Coding Standards

For Mudlet version compatibility and known upstream issues, see [docs/MUDLET_COMPATIBILITY.md](docs/MUDLET_COMPATIBILITY.md).

## Tools
We use a custom Python toolchain for building, validation, and testing. See [docs/PYTHON_TOOLS.md](docs/PYTHON_TOOLS.md) for details on:
- `theGUI/build.py` (assembles `LuminariGUI.xml` from `theGUI/src/`)
- `theGUI/package.py` (`.mpackage` creation and releases)
- `scripts/validate_package.py`
- `tests/run_tests.py`

## Pull Requests
1.  Create a feature branch.
2.  Make your changes to the source fragments in `theGUI/src/` — **not** to `LuminariGUI.xml`, which is a build output.
3.  Build: `python3 theGUI/build.py`.
4.  Run validation: `python3 scripts/validate_package.py`.
5.  Run tests: `python3 tests/run_tests.py`.
6.  Commit both the source fragments and the rebuilt `LuminariGUI.xml`.
7.  Submit PR.

