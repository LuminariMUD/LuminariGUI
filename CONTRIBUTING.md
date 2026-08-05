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

1. Create a feature branch.
2. Make changes to source fragments in `theGUI/src/`, **not** directly to
   `LuminariGUI.xml`.
3. Run the non-mutating validation and drift checks while iterating:

   ```bash
   python3 theGUI/build.py --validate
   python3 theGUI/build.py --diff --fail-on-diff
   ```

4. When source changes are ready, run one intentional
   `python3 theGUI/build.py` and commit the source fragments,
   `theGUI/build.yaml`, generated `LuminariGUI.xml`, and new tracked archive.
5. Install the pinned CI dependencies and run the exact `quality`,
   `build-and-test`, Gitleaks, and Semgrep equivalents in
   [docs/CI.md](docs/CI.md). Do not use `--skip-optional` for the CI-equivalent
   test run.
6. Complete the real-client checklist in
   [docs/MUDLET_SMOKE_TEST.md](docs/MUDLET_SMOKE_TEST.md) when behavior,
   callbacks, input, assets, or layout changed.
7. Submit the pull request and wait for `quality`, `build-and-test`, `gitleaks`,
   `CodeQL`, `Semgrep Lua`, and `dependency-review`. Coverage and Mudlet Xvfb
   are informational.

The protected branch requires the pull request to be current with `master`.
See [docs/CI.md](docs/CI.md) for false-positive handling; do not broadly
disable a scanner or replace an immutable action pin with a floating tag.
