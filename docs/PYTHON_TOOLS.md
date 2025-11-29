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
- **Python 3.8+** (recommended: Python 3.10+)
- **Git** (required for release workflows)
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

# Extract existing XML into fragments (first-time setup)
python3 theGUI/build.py --extract

# Watch mode for active development
python3 theGUI/build.py --watch

# Show what would change
python3 theGUI/build.py --diff

# Show statistics
python3 theGUI/build.py --stats
```

#### Features
- **Fragment Assembly**: Combines XML fragments into single package
- **Auto-Versioning**: Increments build number on each build
- **Archiving**: Automatically archives previous builds to `docs/archive/`
- **Validation**: Validates fragments and final output
- **Watch Mode**: Rebuilds automatically on file changes

### theGUI/package.py - Package Manager

**Purpose**: Creates distributable `.mpackage` files for Mudlet with full release workflow support.

#### Commands

**Create Package:**
```bash
# Create release package (builds XML first, runs tests)
python3 theGUI/package.py create

# Create development package with timestamp
python3 theGUI/package.py create --dev

# Skip build step (use existing XML)
python3 theGUI/package.py create --skip-build

# Skip test suite
python3 theGUI/package.py create --skip-tests
```

**Release Workflow:**
```bash
# Full release workflow (build, test, branch, package, tag)
python3 theGUI/package.py release

# Preview release without changes
python3 theGUI/package.py release --dry-run

# Release and push to remote
python3 theGUI/package.py release --push
```

**Maintenance:**
```bash
# List all packages in Releases/
python3 theGUI/package.py list

# Clean old dev packages (keeps latest 3)
python3 theGUI/package.py clean

# Keep different number of dev packages
python3 theGUI/package.py clean --keep 5
```

#### Release Workflow Steps

The `release` command executes:

1. **Build**: Runs `build.py` to generate fresh XML
2. **Test**: Runs full test suite
3. **Git Check**: Verifies clean repository state
4. **Branch**: Creates `release/v{version}` branch
5. **Package**: Creates `.mpackage` with metadata
6. **Tag**: Creates annotated git tag
7. **Push**: (Optional) Pushes to remote

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
# Run complete test suite
python3 tests/run_tests.py

# Skip tests requiring optional tools (lua, luacheck)
python3 tests/run_tests.py --skip-optional

# Run from tests directory
cd tests && python3 run_tests.py
```

#### Test Suites
- **Lua Syntax**: Validates all Lua code compiles
- **Function Tests**: Unit tests for core functions
- **Event System**: Tests event handlers and MSDP integration
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
# Preview the release workflow
python3 theGUI/package.py release --dry-run

# Execute release (without push)
python3 theGUI/package.py release

# Or release and push in one step
python3 theGUI/package.py release --push
```

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
4. **Test the .mpackage** in Mudlet before pushing

### Maintenance
1. **Clean old dev packages**: `python3 theGUI/package.py clean`
2. **Review packages**: `python3 theGUI/package.py list`

## Related Documentation

- **[Build System Guide](../theGUI/README_theGUI.md)**: Detailed build system documentation
- **[Developer Guide](MUDLET_DEVELOPMENT.md)**: Architecture and best practices
- **[Changelog](CHANGELOG.md)**: Version history
- **[Contributing](../CONTRIBUTING.md)**: Contribution guidelines
