# Contributing to LuminariGUI

Thank you for your interest in contributing!

## Development Guide
Please read [docs/MUDLET_DEVELOPMENT.md](docs/MUDLET_DEVELOPMENT.md) for:
- Project Architecture (Single-File vs Split)
- Development Workflow
- Coding Standards

## Tools
We use a custom Python toolchain for validation and testing. See [docs/PYTHON_TOOLS.md](docs/PYTHON_TOOLS.md) for details on:
- `validate_package.py`
- `run_tests.py`
- `create_package.py`

## Pull Requests
1.  Create a feature branch.
2.  Make your changes to `LuminariGUI.xml`.
3.  Run validation: `python3 scripts/validate_package.py`.
4.  Run tests: `python3 tests/run_tests.py`.
5.  Submit PR.

