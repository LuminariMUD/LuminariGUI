# LuminariGUI Deployment Guide

This guide provides comprehensive installation and deployment instructions for LuminariGUI, designed for both casual MUD players and technical users.

## Table of Contents

- [Quick Start Installation](#quick-start-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Manual Installation](#manual-installation)
- [Post-Installation Configuration](#post-installation-configuration)
- [Advanced Installation Scenarios](#advanced-installation-scenarios)
- [Upgrade Procedures](#upgrade-procedures)
- [Rollback Instructions](#rollback-instructions)

---

## Quick Start Installation

### Prerequisites Check

Before installing LuminariGUI, ensure you have:

✅ **Mudlet Client** (Version 4.10 or higher recommended)
✅ **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
✅ **Internet Connection** (for initial download and MSDP data)
✅ **MUD Account** on a compatible server with MSDP support

### One-Click Installation (Recommended)

1. **Download the Package**
   ```
   Download: LuminariGUI.mpackage from the official repository
   File Size: ~200KB
   ```

2. **Install via Mudlet Package Manager**
   - Open Mudlet client
   - Go to `Packages` → `Package Manager` 
   - Click `Install` button
   - Select downloaded `LuminariGUI.mpackage` file
   - Click `Open` to install

3. **Verify Installation**
   - Look for "LuminariGUI installed successfully" message in main console
   - Check for new GUI elements on screen
   - Verify YATCO chat tabs appear (if applicable)

### First Launch Checklist

After installation, verify these components are working:

- [ ] **Background UI**: LuminariGUI background panel visible
- [ ] **Chat System**: YATCO tabs displaying properly
- [ ] **Gauges**: Health/Mana/Movement bars visible (if MSDP enabled)
- [ ] **Map Integration**: Map display functional (if mapping enabled)
- [ ] **MSDP Connection**: Real-time data updating from server

---

## Platform-Specific Instructions

### Windows Installation

#### **Standard Installation**
1. **Download Location**: Save package to `Downloads` folder
2. **Mudlet Location**: Usually `C:\Program Files\Mudlet\`
3. **Package Directory**: `%APPDATA%\Mudlet\profiles\[ProfileName]\`

#### **Common Windows Issues**
- **Antivirus Interference**: Add Mudlet to antivirus exclusions
- **Permission Errors**: Run Mudlet as Administrator for first install
- **Path Issues**: Ensure no special characters in username/path

#### **Windows-Specific Commands**
```powershell
# Check Mudlet installation
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select DisplayName, DisplayVersion | Where-Object {$_.DisplayName -like "*Mudlet*"}

# Verify package installation
dir "$env:APPDATA\Mudlet\profiles"
```

### macOS Installation

#### **Standard Installation**
1. **Download Location**: Save to `~/Downloads/`
2. **Mudlet Location**: `/Applications/Mudlet.app`
3. **Package Directory**: `~/Library/Application Support/Mudlet/profiles/[ProfileName]/`

#### **macOS-Specific Considerations**
- **Security Settings**: Allow Mudlet in System Preferences → Security & Privacy
- **Gatekeeper**: May need to right-click Mudlet → "Open" for first launch
- **Permissions**: Grant necessary folder access permissions

#### **macOS Terminal Commands**
```bash
# Check Mudlet installation
ls -la /Applications/ | grep -i mudlet

# Verify package location
ls -la ~/Library/Application\ Support/Mudlet/profiles/
```

### Linux Installation

#### **Ubuntu/Debian**
```bash
# Install Mudlet if needed
sudo apt update
sudo apt install mudlet

# Verify installation
mudlet --version
```

#### **Fedora/RHEL**
```bash
# Install Mudlet
sudo dnf install mudlet

# Alternative: AppImage
wget https://www.mudlet.org/wp-content/files/Mudlet-[version]-x86_64.AppImage
chmod +x Mudlet-[version]-x86_64.AppImage
```

#### **Package Directory Locations**
- **Standard**: `~/.local/share/Mudlet/profiles/[ProfileName]/`
- **Flatpak**: `~/.var/app/org.mudlet.Mudlet/data/Mudlet/profiles/[ProfileName]/`
- **AppImage**: Same as standard location

---

## Manual Installation

### When to Use Manual Installation

Use manual installation if:
- Package manager installation fails
- You need custom file placement
- Working with development versions
- Troubleshooting installation issues

### XML Package Installation

1. **Extract Package Contents**
   ```
   Rename: LuminariGUI.mpackage → LuminariGUI.zip
   Extract: Contents to temporary folder
   ```

2. **Locate Profile Directory**
   - Windows: `%APPDATA%\Mudlet\profiles\[ProfileName]\`
   - macOS: `~/Library/Application Support/Mudlet/profiles/[ProfileName]/`
   - Linux: `~/.local/share/Mudlet/profiles/[ProfileName]/`

3. **Manual File Placement**
   ```
   Copy: LuminariGUI.xml → [ProfileDirectory]/
   
   If additional files exist:
   Copy: [PackageName]/ → [ProfileDirectory]/
   ```

4. **Import in Mudlet**
   - Open Mudlet
   - Go to `Packages` → `Package Manager`
   - Click `Import` button
   - Navigate to copied XML file
   - Select and import

### File Structure Verification

After manual installation, verify this structure exists:
```
[ProfileDirectory]/
├── LuminariGUI.xml
├── [ProfileName].xml (your character profile)
└── [additional package files if any]
```

---

## Post-Installation Configuration

### Initial Setup Wizard

1. **Connect to Your MUD**
   ```
   Host: [your.mud.server]
   Port: [usually 4000-4001]
   ```

2. **Enable MSDP (if supported)**
   ```lua
   -- Test MSDP connection
   send("config +msdp")
   
   -- Verify data reception
   display(msdp)
   ```

3. **Configure YATCO Chat**
   - Channels will auto-configure for most servers
   - Manual setup: see CONFIGURATION.md for details

### Configuration Checklist

Complete these steps after installation:

#### **Essential Configuration**
- [ ] **Server Connection**: Verify stable connection to MUD
- [ ] **MSDP Setup**: Confirm real-time data reception
- [ ] **Chat Channels**: Configure desired communication channels
- [ ] **UI Positioning**: Adjust gauge and panel positions

#### **Optional Configuration**
- [ ] **Themes**: Apply custom color schemes
- [ ] **Font Sizes**: Adjust text scaling for readability
- [ ] **Map Integration**: Configure mapping if available
- [ ] **Affect Tracking**: Set up spell/skill monitoring

### Validation Tests

Run these tests to confirm proper installation:

1. **Basic Functionality Test**
   ```lua
   -- In Mudlet command line, test:
   lua print("LuminariGUI:", LuminariGUI and "OK" or "MISSING")
   ```

2. **MSDP Data Test**
   ```lua
   -- Check MSDP data reception
   lua display(msdp.HEALTH or "No MSDP data")
   ```

3. **UI Component Test**
   - Visual verification of gauges updating
   - Chat tabs responding to channel messages
   - Map display (if applicable)

---

## Advanced Installation Scenarios

### Multiple Character Setup

For multiple characters on the same MUD:

1. **Create Separate Profiles**
   - Mudlet: `Settings` → `Profiles` → `New`
   - Name: `[MUDName]-[CharacterName]`

2. **Install Per Profile**
   - Install LuminariGUI in each profile separately
   - Configure settings independently

3. **Shared Configuration (Optional)**
   ```lua
   -- Share settings between characters
   setConfig("SharedSettings", true)
   ```

### Development/Testing Installation

For developers or testers:

1. **Clone Repository**
   ```bash
   git clone [repository-url]
   cd LuminariGUI
   ```

2. **Development Installation**
   ```bash
   # Create symlink (Linux/Mac)
   ln -s $(pwd)/LuminariGUI.xml ~/.local/share/Mudlet/profiles/[ProfileName]/

   # Copy for development (Windows)
   copy LuminariGUI.xml %APPDATA%\Mudlet\profiles\[ProfileName]\
   ```

3. **Enable Debug Mode**
   ```lua
   -- In Mudlet
   lua DEBUG_MODE = true
   ```

---

## Upgrade Procedures

### Version Migration

1. **Backup Current Installation**
   ```bash
   # Backup profile directory
   cp -r [ProfileDirectory] [ProfileDirectory].backup
   ```

2. **Download New Version**
   - Download latest LuminariGUI.mpackage
   - Verify version compatibility

3. **Upgrade Installation**
   - Uninstall current version (optional)
   - Install new version using standard method
   - Apply configuration migration if needed

### Settings Preservation

```lua
-- Export current settings before upgrade
exportConfig("LuminariGUI_backup.json")

-- Import settings after upgrade
importConfig("LuminariGUI_backup.json")
```

### Version Compatibility

- **3.x → 4.x**: Major changes, manual configuration review required
- **4.x → 4.y**: Minor updates, automatic migration
- **Development → Stable**: Export/import settings recommended

---

## Rollback Instructions

### Quick Rollback

1. **Uninstall Current Version**
   - Mudlet: `Packages` → `Package Manager`
   - Select LuminariGUI
   - Click `Uninstall`

2. **Restore Previous Version**
   ```bash
   # Restore from backup
   rm -rf [ProfileDirectory]
   cp -r [ProfileDirectory].backup [ProfileDirectory]
   ```

3. **Restart Mudlet**
   - Close and reopen Mudlet
   - Verify previous version restored

### Clean Uninstall

For complete removal:

1. **Remove Package**
   - Uninstall via Package Manager
   - OR delete XML file manually

2. **Clear Configuration**
   ```lua
   -- Clear LuminariGUI settings
   clearConfig("LuminariGUI")
   ```

3. **Remove Data Files**
   ```bash
   # Remove any cached data
   rm -rf [ProfileDirectory]/LuminariGUI*
   ```

---

## Troubleshooting Installation

### Common Installation Failures

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Package won't install | Error dialog, no GUI changes | Check file integrity, try manual install |
| UI elements missing | No gauges/panels visible | Verify MSDP connection, restart Mudlet |
| Chat system broken | No YATCO tabs | Check YATCO dependency, review logs |
| Performance issues | Lag, slow response | Disable debug mode, check system resources |

### Emergency Recovery

If installation completely breaks Mudlet:

1. **Safe Mode Start**
   ```bash
   mudlet --safe-mode
   ```

2. **Remove Problematic Package**
   - Navigate to profile directory
   - Delete LuminariGUI.xml
   - Restart normally

3. **Profile Reset (Last Resort)**
   ```bash
   # Backup first!
   mv [ProfileDirectory] [ProfileDirectory].broken
   # Create new profile in Mudlet
   ```

---

## Support and Resources

### Getting Help

- **Documentation**: README.md, CONFIGURATION.md, TROUBLESHOOTING.md
- **Issues**: GitHub Issues tracker
- **Community**: MUD forums, Discord channels
- **Email**: [maintainer contact]

### Useful Commands

```lua
-- Check installation status
lua print("LuminariGUI version:", LuminariGUI.version or "Not installed")

-- Reload package (development)
lua uninstallPackage("LuminariGUI"); installPackage("LuminariGUI.xml")

-- Debug information
lua display(LuminariGUI.debug_info())
```

### Next Steps

After successful installation:
1. Read [CONFIGURATION.md](CONFIGURATION.md) for customization options
2. Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. Check [API.md](API.md) for development and scripting

---

*This deployment guide is part of the LuminariGUI documentation suite. For the most current version, visit the official repository.*