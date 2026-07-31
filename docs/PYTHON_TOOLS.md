# LuminariGUI Python Development Tools

## Overview

The LuminariGUI project includes a sophisticated Python toolchain that provides comprehensive development workflow automation, XML management, and release orchestration. These tools work together to streamline the development process from code validation to production releases.

### Tool Suite
- **[`theGUI/build.py`](#theguibuildpy---source-to-build-system)** - Assembles source fragments into LuminariGUI.xml
- **[`theGUI/package.py`](#theguipackagepy---package-manager)** - Creates .mpackage files and manages releases
- **[`scripts/validate_package.py`](#scriptsvalidate_packagepy---package-validation)** - Package validation with Lua syntax checking
- **[`tests/run_tests.py`](#testsrun_testspy---testing-orchestration)** - Comprehensive testing framework

### Key Benefits
- **Integrated Workflow**: Tools work seamlessly together in development and release processes
- **Modular Source**: Edit XML fragments, build automatically assembles them
- **Comprehensive Testing**: Automated testing prevents regression and ensures quality
- **Cross-Platform**: Compatible with Windows, macOS, and Linux
- **Git Integration**: Built-in version control workflow automation

## Installation

### Requirements

#### Core Tools
- **Python 3.10+**
- **Git** (required for release workflows)
- **GitHub CLI (`gh`)** (required to publish and verify the GitHub Release page)
- **Standard Library Only**: No external dependencies for core tools

#### Optional Dependencies
- **PyYAML**: Faster YAML parsing (`pip install pyyaml`)
- **Lua/luac**: Required for Lua syntax validation
- **luacheck**: Optional static analysis

### Verification
```bash
# Check Python version
python3 --version

# Verify tools are executable
python3 theGUI/build.py --help
python3 theGUI/package.py --help
python3 scripts/validate_package.py --help
```

## Tools Reference

### theGUI/build.py - Source-to-Build System

**Purpose**: Assembles modular source fragments from `theGUI/src/` into the final `LuminariGUI.xml` package.

#### Command-Line Usage
```bash
# Build the package (auto-increments version)
python3 theGUI/build.py

# Validate without writing output
python3 theGUI/build.py --validate

# DESTRUCTIVE: replace fragments and build.yaml from the existing XML
python3 theGUI/build.py --extract

# MUTATING: build immediately and version-bump on each detected change
python3 theGUI/build.py --watch

# Show what would change
python3 theGUI/build.py --diff

# Show statistics
python3 theGUI/build.py --stats

# Build an exact version without auto-incrementing
python3 theGUI/build.py --version 2.0.4.029
```

`--validate`, `--diff`, `--stats`, and `--fail-on-diff` are read-only.
`--extract`, `--watch`, and `--clean` mutate or delete repository artifacts.

#### Features
- **Fragment Assembly**: Combines XML fragments into single package
- **Auto-Versioning**: Increments build number on each build
- **Archiving**: Automatically archives previous builds to `docs/archive/`
- **Validation**: Validates fragments and final output
- **Watch Mode**: Rebuilds automatically on file changes

### theGUI/package.py - Package Manager

**Purpose**: Creates local distributable `.mpackage` files and publishes complete release refs and artifacts.

#### Commands

**Create Package:**
```bash
# Create a local distributable package (builds XML first, runs tests)
python3 theGUI/package.py create

# Create development package with timestamp
python3 theGUI/package.py create --dev

# Skip build step (use existing XML)
python3 theGUI/package.py create --skip-build

# Skip test suite
python3 theGUI/package.py create --skip-tests

# Build and package an exact version
python3 theGUI/package.py create --version 2.0.4.029
```

**Release Workflow:**
```bash
# Publish and verify the complete release, including GitHub assets
python3 theGUI/package.py release

# Preview publication without changes
python3 theGUI/package.py release --dry-run

# Publish one exact version across the XML, package, branch, and tag
python3 theGUI/package.py release --version 2.0.4.030
```

`release` always publishes and requires authenticated Git and `gh` access. For
a local artifact without commits, tags, or pushes, use `create`.

**Maintenance:**
```bash
# List all packages in Releases/
python3 theGUI/package.py list

# DESTRUCTIVE: remove old dev packages (keeps latest 3)
python3 theGUI/package.py clean

# Keep different number of dev packages
python3 theGUI/package.py clean --keep 5
```

#### Release Workflow Steps

The `release` command executes:

1. **Git Preflight**: Verifies the user's repository is clean before creating build changes
2. **Build**: Runs `build.py` to generate fresh XML and resolves the release version
3. **Test**: Runs the available test suites
4. **Branch**: Creates `release/v{version}` branch
5. **Package**: Creates and commits `.mpackage` plus metadata
6. **Tag**: Creates annotated git tag
7. **Merge**: Merges the release branch into `master`
8. **Publish**: Atomically pushes `master`, the release branch, and tag to `origin`
9. **Verify refs**: Confirms all three remote refs match their local release refs
10. **GitHub Release**: Publishes the release page and attaches `.mpackage` plus JSON metadata
11. **Verify assets**: Confirms the page is public and both assets are uploaded

An explicit `--version` is propagated through `build.yaml`, the built XML,
package metadata, branch, and tag. When `--skip-build` is used, packaging
fails if the selected version does not match the version embedded in the XML.
There is no commit-without-push release mode.

#### Package Output Structure
```
Releases/
├── LuminariGUI-v2.0.4.019.mpackage      # Release package
├── LuminariGUI-v2.0.4.019.json          # Release metadata
├── LuminariGUI-v2.0.4.019-dev-*.mpackage # Dev packages
└── LuminariGUI-v2.0.4.019-dev-*.json    # Dev metadata
```

### scripts/validate_package.py - Package Validation

**Purpose**: Validates Mudlet packages for XML structure and Lua syntax.

#### Command-Line Usage
```bash
# Validate LuminariGUI.xml (includes Lua syntax)
python3 scripts/validate_package.py

# Validate specific file
python3 scripts/validate_package.py path/to/file.xml

# Skip Lua syntax checking
python3 scripts/validate_package.py --no-lua-syntax
```

#### Features
- **XML Validation**: Checks structure and required elements
- **Lua Syntax**: Validates all embedded Lua code using luac
- **Issue Detection**: Finds common problems like unescaped characters

### tests/run_tests.py - Testing Orchestration

**Purpose**: Runs comprehensive test suite for code quality assurance.

#### Command-Line Usage
```bash
# Run the complete suite (fails before testing if an external tool is missing)
python3 tests/run_tests.py

# Run every suite supported by the installed external tools
python3 tests/run_tests.py --skip-optional

# Run from tests directory
cd tests && python3 run_tests.py

# Add runner configuration or reduce output to one status line
python3 tests/run_tests.py --skip-optional --verbose
python3 tests/run_tests.py --skip-optional --quiet
```

#### Test Suites
- **Lua Syntax**: Validates all Lua code compiles
- **Function Tests**: Unit tests for core functions
- **Event System**: Tests event handlers and MSDP integration
- **Lifecycle Regressions**: Tests upgrade/reset handling and tooling invariants
- **System Tests**: Memory leak detection, error boundaries
- **Performance**: Benchmarks for critical operations

## Development Workflows

### Daily Development

```bash
# 1. Edit source fragments in theGUI/src/
# 2. Validate changes
python3 theGUI/build.py --validate

# 3. Build package
python3 theGUI/build.py

# 4. Create dev package for testing
python3 theGUI/package.py create --dev

# 5. Test in Mudlet
```

### Creating a Release

```bash
# Preview the publishing workflow
python3 theGUI/package.py release --dry-run

# Build, publish, and verify the complete release
python3 theGUI/package.py release

# Independently verify the public release and uploaded assets
gh release view v2.0.4.030 \
  --json url,isDraft,isPrerelease,tagName,assets
```

The command does not report success until the remote refs are present and the
GitHub Release is published (not a draft) with both assets in the `uploaded`
state. Independently verify that state before handing off a release.

### Quick Package Creation

```bash
# Just create a package from current XML
python3 theGUI/package.py create --skip-build --skip-tests
```

## Troubleshooting

### Build Failures
```bash
# Check fragment validity
python3 theGUI/build.py --validate

# See what would change
python3 theGUI/build.py --diff
```

### Test Failures
```bash
# Run with skip-optional if missing lua tools
python3 tests/run_tests.py --skip-optional
```

### Git Issues
```bash
# Skip git check for quick packaging
python3 theGUI/package.py create --skip-build

# Or for release workflow
python3 theGUI/package.py release --skip-git-check
```

## Exit Codes

| Tool | Code 0 | Code 1 |
|------|--------|--------|
| `build.py` | Build successful | Validation or write failure |
| `package.py` | Operation successful | Error during operation |
| `validate_package.py` | Validation passed | Validation failed |
| `run_tests.py` | All tests passed | One or more failures |

## Best Practices

### Development
1. **Edit source fragments** in `theGUI/src/`, not `LuminariGUI.xml` directly
2. **Validate before committing**: `python3 theGUI/build.py --validate`
3. **Use dev packages for testing**: `python3 theGUI/package.py create --dev`
4. **Run tests regularly**: `python3 tests/run_tests.py`

### Releases
1. **Use the release workflow**: `python3 theGUI/package.py release`
2. **Test with dry-run first**: `python3 theGUI/package.py release --dry-run`
3. **Update CHANGELOG.md** before releasing
4. **Test the .mpackage** in Mudlet before invoking `release`, because the command publishes automatically
5. **Publish and verify the GitHub Release page** with both generated assets

### Maintenance
1. **Clean old dev packages**: `python3 theGUI/package.py clean`
2. **Review packages**: `python3 theGUI/package.py list`

## Related Documentation

- **[Build System Guide](../theGUI/README_theGUI.md)**: Detailed build system documentation
- **[Developer Guide](MUDLET_DEVELOPMENT.md)**: Architecture and best practices
- **[Changelog](CHANGELOG.md)**: Version history
- **[Contributing](../CONTRIBUTING.md)**: Contribution guidelines
