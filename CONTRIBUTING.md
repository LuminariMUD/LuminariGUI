# Contributing to LuminariGUI

Welcome to the LuminariGUI project! We appreciate your interest in contributing to this Mudlet package. This guide will help you get started with development, understand our processes, and make meaningful contributions to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Code Contribution Guidelines](#code-contribution-guidelines)
- [Testing and Validation](#testing-and-validation)
- [Documentation Contributions](#documentation-contributions)
- [Bug Reports and Feature Requests](#bug-reports-and-feature-requests)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Release Process](#release-process)
- [Community Guidelines](#community-guidelines)

---

## Getting Started

### Ways to Contribute

We welcome various types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new functionality or improvements
- 💻 **Code Contributions**: Implement features, fix bugs, optimize performance
- 📖 **Documentation**: Improve guides, API docs, examples
- 🎨 **UI/UX**: Enhance visual design and user experience
- 🧪 **Testing**: Create test cases, verify functionality
- 🌍 **Community Support**: Help other users, answer questions

### Before You Start

1. **Read the Documentation**: Familiarize yourself with [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [API.md](API.md)
2. **Check Existing Issues**: Browse [GitHub Issues](../../issues) to see what's already being worked on
3. **Join the Community**: Connect with other contributors via Discord/forums
4. **Understand the Scope**: LuminariGUI is a Mudlet package for MUD clients

---

## Development Environment Setup

### Prerequisites

Before setting up the development environment, ensure you have:

- **Mudlet Client** (4.10 or higher)
- **Git** for version control
- **Text Editor** (VS Code, Sublime Text, Vim, etc.)
- **MUD Server Access** for testing
- **Basic Lua Knowledge** (for code contributions)

### Repository Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/LuminariMUD/LuminariGUI.git
   cd LuminariGUI
   ```

2. **Set Up Upstream Remote**
   ```bash
   git remote add upstream https://github.com/LuminariMUD/LuminariGUI.git
   git fetch upstream
   ```

3. **Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

### Mudlet Development Setup

1. **Development Profile Creation**
   ```
   1. Open Mudlet
   2. Create new profile: "LuminariGUI-Development"
   3. Connect to your test MUD server
   4. Install dependencies (YATCO, etc.)
   ```

2. **Link Development Files**
   ```bash
   # Create symlink to development files (Linux/Mac)
   ln -s /path/to/LuminariGUI/LuminariGUI.xml ~/.local/share/Mudlet/profiles/LuminariGUI-Development/

   # Windows: Copy files to profile directory
   copy LuminariGUI.xml %APPDATA%\Mudlet\profiles\LuminariGUI-Development\
   ```

3. **Enable Debug Mode**
   ```lua
   -- In Mudlet console
   lua LuminariGUI.debug = true
   lua LuminariGUI.development_mode = true
   ```

### Development Tools

#### **Recommended Editor Setup**

For **Visual Studio Code**:
```json
{
  "files.associations": {
    "*.xml": "xml",
    "*.lua": "lua"
  },
  "extensions": {
    "sumneko.lua": "Lua Language Server",
    "redhat.vscode-xml": "XML Language Support"
  }
}
```

#### **Lua Development**
```bash
# Install Lua locally for syntax checking
# Ubuntu/Debian
sudo apt install lua5.1 luarocks

# macOS
brew install lua@5.1 luarocks

# Windows: Download from lua.org
```

#### **Git Hooks Setup**
```bash
# Set up pre-commit hooks
cp .githooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

---

## Code Contribution Guidelines

### Coding Standards

#### **Lua Style Guide**

**Naming Conventions:**
```lua
-- Variables: snake_case
local player_health = 100
local max_mana_points = 250

-- Functions: camelCase
function updatePlayerStats()
    -- implementation
end

-- Constants: UPPER_SNAKE_CASE
local DEFAULT_WINDOW_WIDTH = 800
local MAX_CHAT_LINES = 1000

-- Tables/Objects: PascalCase for constructors, camelCase for instances
local PlayerGauge = {}
local healthGauge = PlayerGauge:new()
```

**Indentation and Formatting:**
```lua
-- Use 4 spaces for indentation, no tabs
function LuminariGUI.complexFunction(param1, param2, options)
    if not param1 then
        error("param1 is required")
    end
    
    local result = {
        success = false,
        data = nil,
        errors = {}
    }
    
    -- Align table values
    local config = {
        width       = options.width or 100,
        height      = options.height or 50,
        background  = options.background or "black",
        foreground  = options.foreground or "white"
    }
    
    return result
end
```

**Error Handling:**
```lua
-- Always validate inputs
function LuminariGUI.createGauge(name, options)
    if not name or type(name) ~= "string" then
        error("Gauge name must be a non-empty string")
    end
    
    if not options or type(options) ~= "table" then
        error("Options must be a table")
    end
    
    -- Safe property access
    local width = options.width or LuminariGUI.DEFAULT_GAUGE_WIDTH
    local height = options.height or LuminariGUI.DEFAULT_GAUGE_HEIGHT
    
    -- Error recovery
    local success, gauge = pcall(Geyser.Gauge, name, options)
    if not success then
        LuminariGUI.logError("Failed to create gauge: " .. name)
        return nil
    end
    
    return gauge
end
```

#### **XML Structure Guidelines**

**Package Organization:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE MudletPackage>
<MudletPackage version="1.001">
  
  <!-- Metadata -->
  <Package>
    <name>LuminariGUI</name>
    <version>1.0.0</version>
    <description>Advanced GUI package for Luminari MUD</description>
    <author>Your Name</author>
  </Package>
  
  <!-- Scripts: Organized by functionality -->
  <Script isActive="yes" isFolder="yes">
    <name>LuminariGUI Core</name>
    
    <Script isActive="yes" isFolder="yes">
      <name>Initialization</name>
      <!-- Initialization scripts -->
    </Script>
    
    <Script isActive="yes" isFolder="yes">
      <name>UI Components</name>
      <!-- UI-related scripts -->
    </Script>
    
    <!-- More organized folders -->
  </Script>
  
  <!-- Triggers: Grouped by purpose -->
  <Trigger isActive="yes" isFolder="yes">
    <name>MSDP Triggers</name>
    <!-- MSDP-related triggers -->
  </Trigger>
  
</MudletPackage>
```

#### **Documentation Standards**

**Function Documentation:**
```lua
--- Creates a new gauge widget with specified properties
-- @param name string: Unique identifier for the gauge
-- @param options table: Configuration options
-- @param options.width number: Width in pixels (default: 100)
-- @param options.height number: Height in pixels (default: 20)
-- @param options.x number: X position (default: 0)
-- @param options.y number: Y position (default: 0)
-- @return Gauge|nil: Created gauge object or nil on failure
-- @usage local healthGauge = LuminariGUI.createGauge("health", {width=200, height=30})
function LuminariGUI.createGauge(name, options)
    -- Implementation
end
```

**Module Documentation:**
```lua
--- LuminariGUI Chat Module
-- Handles chat window management and message routing using YATCO framework
-- 
-- Dependencies:
--   - YATCO (Yet Another Tabbed Chat Option)
--   - Geyser UI framework
--
-- Configuration:
--   - Chat channels defined in LuminariGUI.chat_config
--   - Window positioning in LuminariGUI.chat_layout
--
-- @module LuminariGUI.Chat
-- @author Your Name
-- @version 1.0.0

LuminariGUI.Chat = LuminariGUI.Chat or {}
```

### Architecture Guidelines

#### **Modular Design**

**Module Structure:**
```lua
-- Each module should be self-contained
LuminariGUI.ModuleName = LuminariGUI.ModuleName or {}
local module = LuminariGUI.ModuleName

-- Module initialization
function module.initialize(config)
    module.config = config or {}
    module.setupEvents()
    module.createUI()
end

-- Module cleanup
function module.cleanup()
    module.destroyUI()
    module.removeEvents()
end

-- Public API
function module.publicMethod()
    -- Implementation
end

-- Private functions (local scope)
local function privateHelper()
    -- Helper implementation
end
```

#### **Event-Driven Architecture**

**Event Handling:**
```lua
-- Register events consistently
function LuminariGUI.setupEvents()
    LuminariGUI.event_handlers = LuminariGUI.event_handlers or {}
    
    -- Store handler IDs for cleanup
    local handler_id = registerAnonymousEventHandler("msdp", LuminariGUI.handleMSDP)
    table.insert(LuminariGUI.event_handlers, handler_id)
end

-- Clean event handling
function LuminariGUI.handleMSDP()
    if not msdp then return end
    
    -- Process MSDP data
    LuminariGUI.updateGauges()
    LuminariGUI.updateAffects()
    
    -- Emit custom events
    raiseEvent("LuminariGUI.StatsUpdated", msdp)
end
```

#### **Configuration Management**

**Configuration Pattern:**
```lua
-- Default configuration
LuminariGUI.DEFAULT_CONFIG = {
    ui = {
        theme = "default",
        scale = 1.0,
        position = "right"
    },
    gauges = {
        update_interval = 100,
        show_percentages = true
    },
    chat = {
        max_lines = 1000,
        timestamp_format = "[%H:%M:%S]"
    }
}

-- Configuration loading
function LuminariGUI.loadConfig()
    local saved_config = getConfig("LuminariGUI") or {}
    LuminariGUI.config = table.merge(LuminariGUI.DEFAULT_CONFIG, saved_config)
end

-- Configuration saving
function LuminariGUI.saveConfig()
    setConfig("LuminariGUI", LuminariGUI.config)
end
```

---

## Testing and Validation

### Testing Framework

#### **Unit Testing Setup**

Create test files in `tests/` directory:
```lua
-- tests/test_gauges.lua
local luaunit = require('luaunit')

-- Mock Mudlet functions for testing
local function mockMudletAPI()
    _G.Geyser = {
        Gauge = function(name, options)
            return {
                name = name,
                options = options,
                setValue = function(self, value, max) 
                    self.value = value
                    self.max = max
                end
            }
        end
    }
end

TestGauges = {}

function TestGauges:setUp()
    mockMudletAPI()
    -- Initialize LuminariGUI for testing
end

function TestGauges:testCreateGauge()
    local gauge = LuminariGUI.createGauge("test", {width=100, height=20})
    luaunit.assertNotNil(gauge)
    luaunit.assertEquals(gauge.name, "test")
end

function TestGauges:testGaugeUpdate()
    local gauge = LuminariGUI.createGauge("health", {})
    gauge:setValue(75, 100)
    luaunit.assertEquals(gauge.value, 75)
    luaunit.assertEquals(gauge.max, 100)
end

-- Run tests
os.exit(luaunit.LuaUnit.run())
```

#### **Integration Testing**

**Manual Testing Checklist:**
```
Installation Testing:
□ Fresh Mudlet installation
□ Package installs without errors
□ All UI components appear
□ MSDP connection works
□ Chat system functional

Functionality Testing:
□ Gauges update with stats changes
□ Chat messages route correctly
□ Map integration works
□ Affects display properly
□ Performance acceptable

Compatibility Testing:
□ Windows 10/11
□ macOS (latest 2 versions)
□ Linux (Ubuntu, Fedora)
□ Mudlet versions 4.10+

Stress Testing:
□ Heavy MSDP traffic
□ Many chat messages
□ Extended play sessions
□ Multiple character profiles
```

#### **Automated Testing**

**GitHub Actions Workflow:**
```yaml
# .github/workflows/test.yml
name: LuminariGUI Tests

on: [push, pull_request]

jobs:
  lua-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Lua
      uses: leafo/gh-actions-lua@v8
      with:
        luaVersion: "5.1"
    - name: Install dependencies
      run: |
        sudo apt-get install luarocks
        luarocks install luaunit
    - name: Run tests
      run: lua tests/run_all_tests.lua
      
  xml-validation:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Validate XML
      run: xmllint --noout LuminariGUI.xml
```

### Performance Testing

#### **Benchmarking**
```lua
-- Performance test suite
function LuminariGUI.performanceTest()
    local results = {}
    
    -- Test gauge update performance
    local start_time = os.clock()
    for i = 1, 1000 do
        LuminariGUI.updateGauges()
    end
    results.gauge_updates = (os.clock() - start_time) * 1000
    
    -- Test UI render performance
    start_time = os.clock()
    LuminariGUI.refreshUI()
    results.ui_refresh = (os.clock() - start_time) * 1000
    
    -- Memory usage
    collectgarbage("collect")
    results.memory_kb = collectgarbage("count")
    
    print("Performance Test Results:")
    for test, value in pairs(results) do
        print(string.format("  %s: %.2f", test, value))
    end
    
    return results
end
```

---

## Documentation Contributions

### Documentation Types

#### **User Documentation**
- **README.md**: Overview and basic usage
- **CONFIGURATION.md**: Advanced configuration options
- **DEPLOYMENT.md**: Installation and setup procedures
- **TROUBLESHOOTING.md**: Problem diagnosis and solutions

#### **Developer Documentation**
- **ARCHITECTURE.md**: System design and component relationships
- **API.md**: Code interface documentation
- **CONTRIBUTING.md**: This guide for contributors

#### **Inline Documentation**
- Function/method comments
- Code examples
- Configuration examples

### Documentation Standards

#### **Markdown Style Guide**

**Headers and Structure:**
```markdown
# Main Title (H1)

## Major Sections (H2)

### Subsections (H3)

#### Details (H4)

##### Minor Details (H5)
```

**Code Examples:**
```markdown
<!-- Inline code -->
Use the `LuminariGUI.createGauge()` function.

<!-- Code blocks with language -->
```lua
function LuminariGUI.example()
    print("This is a code example")
end
```

<!-- Command line examples -->
```bash
git clone repository
cd directory
```
```

**Cross-References:**
```markdown
<!-- Link to other docs -->
See [CONFIGURATION.md](CONFIGURATION.md) for details.

<!-- Link to specific sections -->
Review the [Installation Process](#installation-process) above.

<!-- External links -->
Visit [Mudlet Documentation](https://wiki.mudlet.org/)
```

#### **API Documentation Format**

Use consistent format for API documentation:
```lua
--- Brief description of the function
-- Detailed description with usage examples and important notes.
-- Multiple lines provide context about when and how to use this function.
--
-- @param param_name type: Description of parameter
-- @param optional_param type|nil: Description (optional, default: value)
-- @return return_type: Description of return value
-- @return nil: Returned on error conditions
-- @raises error_type: When this error condition occurs
-- @since version: When this function was added
-- @see related_function: Reference to related functionality
-- @usage example_usage: LuminariGUI.functionName(param1, param2)
-- @example
-- -- Create a health gauge
-- local gauge = LuminariGUI.createGauge("health", {
--     width = 200,
--     height = 30,
--     x = 10,
--     y = 10
-- })
function LuminariGUI.functionName(param_name, optional_param)
```

---

## Bug Reports and Feature Requests

### Bug Report Template

When reporting bugs, use this template:

```markdown
## Bug Report

**Description**
A clear and concise description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Actual Behavior**
What actually happened instead.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g. Windows 10, macOS 12.1, Ubuntu 20.04]
- Mudlet Version: [e.g. 4.15.1]
- LuminariGUI Version: [e.g. 1.2.3]
- MUD Server: [e.g. Luminari MUD]

**Debug Information**
```lua
-- Run this in Mudlet and paste output:
lua LuminariGUI.systemDiagnostic()
```

**Additional Context**
Add any other context about the problem here.
```

### Feature Request Template

```markdown
## Feature Request

**Is your feature request related to a problem?**
A clear description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation Ideas**
If you have ideas about how this could be implemented, share them here.
```

### Issue Labels

Use appropriate labels for issues:

- **Type**: `bug`, `enhancement`, `question`, `documentation`
- **Priority**: `low`, `medium`, `high`, `critical`
- **Status**: `needs-investigation`, `in-progress`, `waiting-for-feedback`
- **Component**: `ui`, `msdp`, `chat`, `gauges`, `mapping`
- **Difficulty**: `good-first-issue`, `help-wanted`, `advanced`

---

## Pull Request Process

### Before Creating a Pull Request

1. **Update from Upstream**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run Tests**
   ```bash
   # Run test suite
   lua tests/run_all_tests.lua
   
   # Validate XML
   xmllint --noout LuminariGUI.xml
   
   # Check Lua syntax
   luac -p *.lua
   ```

3. **Update Documentation**
   - Update relevant documentation files
   - Add/update API documentation
   - Include examples for new features

### Pull Request Template

```markdown
## Description

Brief description of changes made.

**Type of Change**
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

**Test Environment**
- OS: [e.g. Windows 10]
- Mudlet Version: [e.g. 4.15.1]
- MUD Server: [e.g. Luminari MUD]

**Testing Performed**
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

**Test Cases**
Describe specific test cases you ran:
1. Test case 1
2. Test case 2

## Screenshots

If applicable, add screenshots showing the changes.

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Related Issues

Fixes #(issue number)
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code style validation
   - XML validation
   - Documentation checks

2. **Manual Review**
   - Code quality assessment
   - Architecture compliance
   - Performance impact review
   - User experience evaluation

3. **Testing Verification**
   - Reviewer tests changes
   - Multiple environment testing
   - Edge case verification

---

## Code Review Guidelines

### For Authors

#### **Preparing for Review**

1. **Self-Review First**
   ```
   □ Check code formatting and style
   □ Verify all tests pass
   □ Ensure documentation is updated
   □ Remove debug code and comments
   □ Verify commit messages are clear
   ```

2. **Small, Focused Changes**
   - Keep PRs under 400 lines when possible
   - Focus on single feature/bug fix
   - Split large changes into multiple PRs

3. **Clear Description**
   - Explain what changes were made and why
   - Include screenshots for UI changes
   - Reference related issues
   - Note any breaking changes

#### **Responding to Feedback**

1. **Be Responsive**
   - Respond to feedback within 48 hours
   - Ask for clarification when needed
   - Address all feedback before requesting re-review

2. **Make Changes Thoughtfully**
   - Consider the reviewer's perspective
   - Explain if you disagree with suggestions
   - Update tests and documentation as needed

### For Reviewers

#### **Review Checklist**

**Code Quality:**
```
□ Code follows style guidelines
□ Logic is clear and efficient
□ Error handling is appropriate
□ No obvious bugs or issues
□ Performance impact acceptable
```

**Architecture:**
```
□ Changes fit existing architecture
□ Modularity and separation maintained
□ Event handling done correctly
□ Configuration managed properly
```

**Testing:**
```
□ Adequate test coverage
□ Tests actually verify functionality
□ Edge cases considered
□ Manual testing performed
```

**Documentation:**
```
□ API documentation updated
□ User documentation reflects changes
□ Code comments explain complex logic
□ Examples provided for new features
```

#### **Review Feedback Guidelines**

1. **Be Constructive**
   ```
   ❌ "This is wrong"
   ✅ "Consider using X pattern here because..."
   ```

2. **Explain Reasoning**
   ```
   ❌ "Change this"
   ✅ "This could cause performance issues when... Consider..."
   ```

3. **Suggest Solutions**
   ```
   ❌ "This doesn't work"
   ✅ "This might not handle edge case X. What about..."
   ```

4. **Recognize Good Work**
   ```
   ✅ "Nice optimization here!"
   ✅ "Good error handling"
   ✅ "Clear and well-documented"
   ```

#### **Review Priority Levels**

- **🔴 Must Fix**: Blocking issues that prevent merge
- **🟡 Should Fix**: Important improvements, but not blocking
- **🟢 Consider**: Suggestions for future improvement
- **💭 Question**: Seeking clarification or discussion

---

## Release Process

### Version Numbering

LuminariGUI follows Semantic Versioning (SemVer):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **Major**: Breaking changes, major feature additions
- **Minor**: New features, backward-compatible changes
- **Patch**: Bug fixes, small improvements

### Release Workflow

#### **Development Releases**

1. **Feature Branches**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git push origin feature/new-feature
   # Create PR to main
   ```

2. **Integration Testing**
   - Automated tests run on PR
   - Manual testing by maintainers
   - Community testing (pre-release)

#### **Stable Releases**

1. **Release Preparation**
   ```bash
   # Update version numbers
   # Update changelog
   # Update documentation
   git checkout -b release/v1.2.3
   ```

2. **Release Checklist**
   ```
   □ All tests passing
   □ Documentation updated
   □ Changelog completed
   □ Version numbers updated
   □ Security review completed
   □ Performance benchmarks run
   □ Breaking changes documented
   ```

3. **Release Process**
   ```bash
   # Tag release
   git tag -a v1.2.3 -m "Release version 1.2.3"
   git push origin v1.2.3
   
   # Create GitHub release
   # Upload package files
   # Notify community
   ```

For detailed package preparation instructions, see [PACKAGING.md](PACKAGING.md).

### Changelog Format

```markdown
# Changelog

## [1.2.3] - 2024-01-15

### Added
- New gauge animation system
- Support for custom color themes
- Export/import configuration functionality

### Changed
- Improved MSDP connection reliability
- Updated UI scaling algorithm
- Enhanced error messages

### Fixed
- Fixed gauge positioning on high-DPI displays
- Resolved chat window memory leak
- Corrected map integration issues

### Deprecated
- Old theme configuration format (use new format)

### Removed
- Experimental feature X (replaced by Y)

### Security
- Fixed potential script injection vulnerability
```

---

## Community Guidelines

### Code of Conduct

#### **Our Pledge**

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

#### **Expected Behavior**

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

#### **Unacceptable Behavior**

- Harassment, trolling, or derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Communication Channels

#### **GitHub Issues**
- Bug reports and feature requests
- Technical discussions about implementation
- Documentation improvements

#### **Discussions/Forums**
- General questions and help
- Community showcase
- Project announcements

#### **Real-time Chat**
- Discord/IRC for immediate help
- Coordination among contributors
- Casual community interaction

### Community Roles

#### **Users**
- Report bugs and request features
- Provide feedback and testing
- Help other users
- Share configurations and tips

#### **Contributors**
- Submit code improvements
- Improve documentation
- Review pull requests
- Mentor new contributors

#### **Maintainers**
- Guide project direction
- Review and merge contributions
- Manage releases
- Moderate community interactions

### Getting Help

#### **For Users**
1. Check existing documentation
2. Search GitHub issues
3. Ask in community forums
4. Create detailed bug report

#### **For Contributors**
1. Read contribution guidelines
2. Start with "good first issue" labels
3. Ask questions in discussions
4. Join community chat for real-time help

### Recognition

We believe in recognizing contributions:

- **Contributors file**: All contributors listed
- **Release notes**: Major contributors highlighted
- **Community showcase**: Featured implementations
- **Badges/titles**: Recognition for sustained contribution

---

## Legal and Licensing

### License Agreement

By contributing to LuminariGUI, you agree that your contributions will be licensed under the same license as the project (specify license here).

### Copyright

- Retain copyright to your contributions
- Grant project license to use contributions
- Ensure you have rights to contribute code

### Third-Party Code

- Must be compatible with project license
- Include appropriate attribution
- Document in THIRD_PARTY_NOTICES

---

## Quick Reference

### Common Commands

```bash
# Development setup
git clone your-fork
git remote add upstream original-repo
git checkout -b feature-branch

# Testing
lua tests/run_all_tests.lua
xmllint --noout LuminariGUI.xml

# Submitting changes
git add .
git commit -m "descriptive message"
git push origin feature-branch
# Create PR on GitHub
```

### Useful Resources

- **[Mudlet Documentation](https://wiki.mudlet.org/)**
- **[Lua 5.1 Reference](https://www.lua.org/manual/5.1/)**
- **[Geyser UI Framework](https://github.com/Mudlet/Mudlet/wiki/Manual:Geyser)**
- **[YATCO Chat System](https://github.com/demonnic/yatco)**

### Contact Information

- **Project Maintainer**: [maintainer email]
- **Community Discord**: [discord link]
- **GitHub Issues**: [issues link]
- **Documentation**: [docs link]

---

*Thank you for contributing to LuminariGUI! Your efforts help make this tool better for the entire MUD community.*