# LuminariGUI Package Preparation Guide

This guide explains how to prepare the LuminariGUI package for distribution and release.

## Package Format

LuminariGUI is distributed in two formats:

- **XML Format (`LuminariGUI.xml`)**: Direct import format containing all scripts, triggers, aliases, and configuration data
- **Package Format (`LuminariGUI.mpackage`)**: A ZIP-compressed archive containing XML data, metadata, and resources

### Understanding .mpackage Files

**A .mpackage file is essentially a ZIP archive** that contains:
- **XML configuration files** - Store all triggers, aliases, scripts, timers, etc.
- **config.lua** - Package metadata and configuration
- **Resources folder** - Images, sounds, fonts, and other assets (if any)

The conversion from XML to `.mpackage` is straightforward - Mudlet stores all your work internally as XML, and the package format simply bundles this XML data with metadata into a compressed archive.

## Pre-Release Checklist

Before preparing a package for release, ensure the following steps are completed:

### 1. Code Quality Validation

```bash
# Validate XML structure
python3 validate_xml.py

# Format XML (optional - creates backup)
python3 format_xml.py

# Check for syntax errors
# (Load in Mudlet to test functionality)
```

### 2. Version Management

Update version information in key locations:

**LuminariGUI.xml (header comment):**
```xml
<!-- LuminariGUI Package v2.1.0
     Enhanced MUD client interface for LuminariMUD
     Repository: https://github.com/LuminariMUD/LuminariGUI
     License: Public Domain (Unlicense) -->
```

**CHANGELOG.md:**
- Move unreleased changes to new version section
- Update version number and date
- Ensure all changes are documented

### 3. Documentation Review

- [ ] README.md is up to date
- [ ] QUICK_REFERENCE.md reflects current features
- [ ] All documentation links work correctly
- [ ] Installation instructions are current

## Package Preparation Steps

### Step 1: Clean and Validate

```bash
# Ensure working directory is clean
git status

# Validate XML structure
python3 validate_xml.py
# Should show: ✅ XML validation passed

# Optional: Format XML for consistency
python3 format_xml.py --no-backup
```

### Step 2: Version Update

1. **Update package header comment** in `LuminariGUI.xml`:
   ```xml
   <!-- LuminariGUI Package v[NEW_VERSION]
        Enhanced MUD client interface for LuminariMUD
        Repository: https://github.com/LuminariMUD/LuminariGUI
        License: Public Domain (Unlicense) -->
   ```

2. **Update CHANGELOG.md**:
   - Move unreleased items to new version section
   - Add release date
   - Follow semantic versioning

### Step 3: Testing

**Critical**: Test the package before release:

1. **Load in Mudlet**:
   - Import `LuminariGUI.xml` into a clean Mudlet profile
   - Connect to LuminariMUD
   - Verify all components load correctly

2. **Functional Testing**:
   - Test chat system (YATCO tabs)
   - Verify mapping functionality
   - Check status effect icons
   - Test GUI responsiveness

3. **Error Checking**:
   - Monitor Mudlet error console
   - Check for Lua errors or warnings
   - Verify MSDP data reception

### Step 4: Package Creation

#### Option 1: XML Package (Direct Import)
The `LuminariGUI.xml` file IS the package - no additional build process is needed for manual installation.

#### Option 2: .mpackage Format (For Auto-Install Systems)
For GMCP auto-install and official repository submission, create a .mpackage file:

### How XML Files are Converted to .mpackage Files

The conversion process is straightforward because **Mudlet stores your work internally as XML**:

**Method 1: Using Mudlet's Package Exporter (Recommended)**
1. Load `LuminariGUI.xml` into Mudlet
2. Go to Package Manager → Settings → Package Exporter
3. Select "LuminariGUI" package
4. Click "Export Package"
5. Save as `LuminariGUI.mpackage`

**What happens internally:**
- Mudlet takes the XML data for your selected items
- Creates the package structure with metadata
- Bundles resources (images, sounds, etc.) if any
- Compresses everything into a ZIP archive with `.mpackage` extension

**Method 2: Manual Creation (Advanced)**
Since .mpackage files are ZIP archives, you can create them manually:

```bash
# Create package directory structure
mkdir -p LuminariGUI_package

# Copy XML content (this should be exported from Mudlet properly)
cp LuminariGUI.xml LuminariGUI_package/

# Copy resources if any
cp -r images/ LuminariGUI_package/ 2>/dev/null || true

# Create config.lua with package metadata
cat > LuminariGUI_package/config.lua << 'EOF'
mpackage = "LuminariGUI"
author = "LuminariMUD Team"
title = "LuminariGUI"
description = [[
Enhanced MUD client interface for LuminariMUD with advanced features
including chat management, mapping, status effects, and more.
]]
version = "2.1.0"
created = "2024-01-01"
modified = "2024-01-01"
dependencies = {}
EOF

# Create the ZIP archive (it's just a renamed ZIP file)
cd LuminariGUI_package
zip -r ../LuminariGUI.mpackage *
cd ..
rm -rf LuminariGUI_package

# Or alternatively, create as ZIP and rename
# zip -r LuminariGUI.zip LuminariGUI_package/*
# mv LuminariGUI.zip LuminariGUI.mpackage
```

**Method 3: Using Muddler Build Tool (Alternative Approach)**

Muddler uses a different workflow for package creation:

1. **JSON definitions + Lua scripts** - Define triggers/aliases in JSON, scripts in separate Lua files
2. **Muddler converts JSON to XML** - Build process transforms JSON definitions into Mudlet's XML format
3. **Bundle and compress** - Creates the final `.mpackage` ZIP archive

```json
// Example: triggers.json in Muddler project
{
  "name": "Health Trigger",
  "patterns": ["^Health: (\\d+)/(\\d+)$"],
  "script": "MyPackage.updateHealth(matches[2], matches[3])"
}
```

**Important Notes:**
- **No separate XML-to-mpackage converter needed** - Mudlet handles this internally
- **The .mpackage extension is just convention** - It's actually a ZIP file
- **XML structure is Mudlet-specific** - Don't create XML manually unless you understand Mudlet's schema
- **Use the official tools** - Package Exporter or Muddler handle all the complexity
- **The "conversion" is really just packaging** - Mudlet takes its internal XML representation and bundles it into a distributable ZIP archive

**Package Format Comparison:**
- **LuminariGUI.xml**: Direct import, manual installation, XML format
- **LuminariGUI.mpackage**: Auto-install systems, official repository, ZIP archive containing XML + metadata

**Package Contents Verification**:
```bash
# Check file size (should be substantial)
ls -lh LuminariGUI.xml
ls -lh LuminariGUI.mpackage

# Verify XML structure
head -10 LuminariGUI.xml
tail -10 LuminariGUI.xml

# Check for required components
grep -c "<Trigger" LuminariGUI.xml    # Should show multiple triggers
grep -c "<Script" LuminariGUI.xml     # Should show multiple scripts
grep -c "<Alias" LuminariGUI.xml      # Should show multiple aliases
```

### Viewing Package Contents

Since `.mpackage` files are ZIP archives, you can inspect them directly:

```bash
# List contents of .mpackage file
unzip -l LuminariGUI.mpackage

# Extract to view contents
unzip LuminariGUI.mpackage -d extracted/

# You'll typically see files like:
# - Trigger.xml
# - Alias.xml
# - Script.xml
# - Timer.xml
# - config.lua
# - resources/ (if any images/sounds included)

# View the config.lua metadata
unzip -p LuminariGUI.mpackage config.lua
```

**Example of what you might see:**
```
Archive:  LuminariGUI.mpackage
  Length      Date    Time    Name
---------  ---------- -----   ----
   45230  2024-01-01 12:00   Trigger.xml
   12450  2024-01-01 12:00   Alias.xml
   89120  2024-01-01 12:00   Script.xml
     892  2024-01-01 12:00   config.lua
    2048  2024-01-01 12:00   resources/
    1024  2024-01-01 12:00   resources/icon.png
---------                     -------
  150764                     6 files
```

## Release Process

### Step 1: Create Release Branch

```bash
# Create release branch
git checkout -b release/v[VERSION]

# Commit final changes
git add LuminariGUI.xml CHANGELOG.md
git commit -m "Prepare release v[VERSION]"

# Push release branch
git push origin release/v[VERSION]
```

### Step 2: Create GitHub Release

1. **Tag the release**:
   ```bash
   git tag -a v[VERSION] -m "Release version [VERSION]"
   git push origin v[VERSION]
   ```

2. **Create GitHub Release**:
   - Go to GitHub repository
   - Click "Releases" → "Create a new release"
   - Select the version tag
   - Use changelog content for release notes

3. **Upload Package Files**:
   - Attach `LuminariGUI.xml` to the GitHub release
   - Attach `LuminariGUI.mpackage` for auto-install systems
   - Use filenames: `LuminariGUI-v[VERSION].xml` and `LuminariGUI-v[VERSION].mpackage`
   - Also attach as `LuminariGUI.xml` and `LuminariGUI.mpackage` for direct download compatibility

### Step 3: Post-Release

1. **Merge to main**:
   ```bash
   git checkout master
   git merge release/v[VERSION]
   git push origin master
   ```

2. **Update documentation**:
   - Verify download links in README.md work
   - Update any version references

3. **Community notification**:
   - Announce on LuminariMUD forums
   - Update Discord #mudlet-help channel
   - Notify regular contributors

4. **Server-Side Auto-Install Setup** (If applicable):
   ```lua
   -- Add to LuminariMUD server code (post-login)
   -- Send GMCP package info to Mudlet clients
   send_gmcp(ch, "Client.GUI", json_encode({
       version = "2.1.0",
       url = "https://github.com/LuminariMUD/LuminariGUI/releases/latest/LuminariGUI.mpackage"
   }))
   ```

## Distribution Locations

### Automatic Installation Systems

#### 1. Server-Side GMCP Auto-Install (Recommended)

If you control the LuminariMUD server, implement GMCP-based automatic package installation:

**Server Implementation:**
```lua
-- Send after player login
Client.GUI {
    "version": "2.1.0",
    "url": "https://luminarimud.com/packages/LuminariGUI.mpackage"
}
```

**Benefits:**
- Automatic updates when players connect
- No manual installation required
- Version checking and updates
- Seamless user experience

#### 2. Official Mudlet Package Repository

Submit to the **Official Mudlet Package Repository** for maximum visibility:

**Submission Methods:**
- **Web Upload**: Visit [packages.mudlet.org/upload](https://packages.mudlet.org/upload)
- **GitHub PR**: Fork [mudlet-package-repository](https://github.com/Mudlet/mudlet-package-repository)

**Repository Benefits:**
- Searchable by all Mudlet users
- Automatic updates via Mudlet Package Manager
- Quality validation by Mudlet team
- Maximum distribution reach

**Repository Requirements:**
- Comprehensive documentation (✅ we have this)
- Clear versioning (✅ semantic versioning)
- Proper dependency declarations
- Tested on multiple platforms

### Manual Distribution Methods

#### Primary Distribution
- **GitHub Releases**: Primary download location
- **Direct XML**: https://github.com/LuminariMUD/LuminariGUI/releases/latest/LuminariGUI.xml

### Installation Methods

**Method 1: Direct Download**
```bash
wget https://github.com/LuminariMUD/LuminariGUI/releases/latest/LuminariGUI.xml
# Then import via Mudlet Package Manager
```

**Method 2: Clone Repository**
```bash
git clone https://github.com/LuminariMUD/LuminariGUI.git
# Use LuminariGUI.xml from repository
```

## Package Validation

After release, validate the package:

1. **Download Test**:
   ```bash
   # Test direct download
   wget https://github.com/LuminariMUD/LuminariGUI/releases/latest/LuminariGUI.xml -O test-download.xml
   
   # Validate downloaded file
   python3 validate_xml.py test-download.xml
   ```

2. **Installation Test**:
   - Create fresh Mudlet profile
   - Install downloaded package
   - Connect to LuminariMUD
   - Verify functionality

## Troubleshooting Package Issues

### Common Problems

**XML Validation Fails**:
- Check for unescaped characters (`<`, `>`, `&`)
- Verify comment block structure
- Ensure all tags are properly closed

**Package Won't Load in Mudlet**:
- Check XML header and DOCTYPE
- Verify MudletPackage version compatibility
- Look for syntax errors in embedded Lua scripts

**.mpackage File Issues**:
- **File won't open**: Remember .mpackage files are ZIP archives - check if the file is corrupted
- **Missing config.lua**: Ensure the package has proper metadata file
- **Incomplete extraction**: Some ZIP tools may not handle all files properly

**Missing Components After Install**:
- Verify all package sections are present
- Check for incomplete XML structure
- Ensure file wasn't truncated during download
- For .mpackage files, extract and verify ZIP contents are complete

**Manual Package Creation Issues**:
- **XML structure mismatch**: Don't create XML manually - use Mudlet's Package Exporter
- **Missing dependencies**: Ensure all required resources are included
- **Improper ZIP structure**: .mpackage files need specific internal structure

### Support Resources

- **Validation Tool**: `python3 validate_xml.py`
- **Format Tool**: `python3 format_xml.py`
- **Issue Tracker**: GitHub Issues
- **Community**: LuminariMUD Discord #mudlet-help

## Key Points Summary

### Understanding Package Formats

**The Essential Truth About .mpackage Files:**
- A `.mpackage` file is **just a ZIP archive** with XML content inside
- No special conversion tools needed - Mudlet handles everything internally
- The XML format is what Mudlet uses to store all your triggers, aliases, and scripts

### Conversion Process Reality

**From XML to .mpackage:**
1. **Mudlet stores everything as XML internally** (your triggers, aliases, scripts)
2. **Package Exporter bundles XML + metadata** into a ZIP structure
3. **ZIP file gets .mpackage extension** (but it's still just a ZIP)

**From .mpackage back to components:**
1. **Extract the ZIP** to see individual XML files
2. **Each XML file contains** specific component types (triggers, aliases, etc.)
3. **Mudlet reads the XML** and recreates your package components

### Distribution Strategy

**Two formats serve different purposes:**
- **`LuminariGUI.xml`**: Direct import, manual installation, development/testing
- **`LuminariGUI.mpackage`**: Auto-install systems, official repositories, end users

**Best practices:**
- Use **Package Exporter** for creating .mpackage files
- Test both formats before release
- Manual ZIP creation only if you understand Mudlet's XML schema
- Always include proper `config.lua` metadata in .mpackage files

This makes packages portable and easy to share while maintaining all the configuration data needed to recreate your triggers, aliases, and scripts in another Mudlet installation.

## Version History

Track significant packaging changes:

- **v2.0.0**: Added XML validation tools
- **v1.0.0**: Initial release structure

For detailed change history, see [CHANGELOG.md](CHANGELOG.md).