# NyyLIB013dev Sound System Documentation

This document provides a comprehensive reference for all sound-related techniques and implementations in the NyyLIB013dev.xml package.

## Overview
The NyyLIB013dev sound system provides audio feedback for key game events including:
- Player communications (tells, petitions)
- Combat events (stuns, deaths, bashes)
- Status changes (buffs, resurrection)
- Environmental effects (dragons, fire)
- Item interactions (looting, corpse dragging)

The system supports three modes: **off** (no sounds), **limited** (critical sounds only), and **on** (all sounds). Sound files are sourced from freesound.org and follow their naming convention.

## Table of Contents
1. [Core Sound Functions](#core-sound-functions)
2. [Sound Configuration System](#sound-configuration-system)
3. [Sound Categories and Usage](#sound-categories-and-usage)
4. [Implementation Patterns](#implementation-patterns)
5. [Sound File Reference](#sound-file-reference)
6. [Debug and Testing](#debug-and-testing)
7. [File System Notes](#file-system-notes)
8. [Best Practices](#best-practices)
9. [Integration with LuminariGUI](#integration-with-luminarigui)

## Core Sound Functions

### 1. `sound(xname, xvolume, xlimited)`
The primary function for playing sounds in the system.

**Parameters:**
- `xname` (string): Filename of the sound to play
- `xvolume` (number): Volume level (default: 100)
- `xlimited` (boolean): If true, sound plays even in "limited" mode

**Behavior:**
- Checks the current sound mode setting from `charData:get("sound")`
- In "off" mode: No sounds play
- In "limited" mode: Only sounds with `xlimited=true` play (tells, petitions)
- In "on" mode: All sounds play
- Respects the `noSound` variable for one-time silencing
- Outputs debug information when sounds play

**Example Usage:**
```lua
sound("365641__furbyguy__8-bit-alarm.wav", nil, true)  -- Limited sound (plays in all modes except off)
sound("85568__joelaudio__dragon-roar.wav")              -- Normal sound (only in "on" mode)
sound("105308__kovrov__rumble.wav", 50)                 -- Half volume
```

### 2. `soundpath(xname)`
Resolves the full path to a sound file.

**Function:**
```lua
function soundpath(xname)
  local pathname = string.gsub(NyyLIB.homedir .. "sounds\\" .. xname, "\\", "/")
  local is_file = io.open(pathname)
  if is_file == nil then
    cecho("<red>[Error: file " .. pathname .. " not found]\n")
  else
    io.close(is_file)
  end
  return pathname
end
```

**Features:**
- Constructs path from `NyyLIB.homedir` + "sounds\" + filename
- Converts backslashes to forward slashes for compatibility
- Validates file existence and reports errors

### 3. `noSound` Variable
Global variable for temporary sound suppression.

**Usage:**
```lua
noSound = true  -- Suppress the next sound
-- Next sound() call will be silent and reset noSound to false
```

**Common Uses:**
- Preventing sounds during automated actions (wormhole, rift)
- One-time sound suppression without changing settings

**Implementation Examples:**
```lua
-- Wormhole automation suppresses sound
if charData:get("wormhole") then
  eraseLine()
  noSound = true
  mud:send("worm " .. target)
end

-- Rift automation suppresses sound
if charData:get("wormhole") then
  eraseLine()
  noSound = true
  mud:send("rift " .. target)
  NyyLIB.psilag="rift"
end
```

## Sound Configuration System

### Settings Structure
Sound configuration is defined in the `setvar` table during initialization:
```lua
{ "sound", "", {"off", "limited", "on"}, "on", "play sounds"}
```
- **Parameter 1**: Variable name ("sound")
- **Parameter 2**: Class restriction (empty = all classes)
- **Parameter 3**: Valid values array
- **Parameter 4**: Default value ("on")
- **Parameter 5**: Description

### Sound Modes
1. **"off"**: All sounds disabled
2. **"limited"**: Only critical sounds (tells, petitions) with `xlimited=true`
3. **"on"**: All sounds enabled (default)

### Configuration Access
```lua
local soundmode = charData:get("sound", false)
```

## Sound Categories and Usage

### 1. Communication Sounds
Plays for important player communications.

| Sound File | Trigger | Limited |
|------------|---------|---------|
| 365641__furbyguy__8-bit-alarm.wav | Petition responses, roller alerts | Yes |
| 320181__dland__hint.wav | Direct tells ("tells you") | Yes |
| 72127__kizilsungur__sweetalertsound3.wav | NPC attention messages ("An ogre shaman from Faang watches you closely") | No |

### 2. Combat Sounds
Various combat-related audio feedback.

| Sound File | Trigger Context |
|------------|-----------------|
| 274736__sforsman__distort-ring-2.wav | Stun effects ("The world starts spinning, and your ears are ringing!") |
| 195954_minian89_death-blood-splatter.wav | Death of group members (except Lilithelle) |
| 209740__yummie__minion-yahoo-2.wav | Lilithelle's death (special character) |
| 123753__vicces1212__collapse.wav | Stand triggers (earthquake, slam, sprawling effects) |
| 241280__sonictechtonic__gooeybashes.wav | Bash recovery messages |
| 86324__timbre__smashing-1b.wav | Mirror image destruction (general) |
| 86324__timbre__smashing-1a.wav | Player's own mirror image being hit |
| 368014__trngle__burning-match-into-water.wav | Burn damage ("You are burned as you hit") |

### 3. Environmental/Creature Sounds
Atmospheric and creature-specific sounds.

| Sound File | Trigger |
|------------|---------|
| 85568__joelaudio__dragon-roar.wav | Dragon roar attacks (various dragon breath/roar messages) |
| 45809__themfish__gas-fire-catch.wav | Inferno sound trigger |

### 4. Status/Buff Sounds
Status changes and magical effects.

| Sound File | Trigger |
|------------|---------|
| 105308__kovrov__rumble.wav | Supple girdle activation ("You feel yourself growing, in strength and size") |
| 165331__ani-music__tubular-bell-of-death.wav | Player death ("Your soul is transported to The Fugue Plane") |
| 139025__rj10328__131659-bertrof-game-sound-intro-to-game-80921-justinbw-buttonchime02up-4.wav | Resurrection (various resurrection messages) |

### 5. Action/Item Sounds
Player actions and item interactions.

| Sound File | Trigger |
|------------|---------|
| 343462__rocotilos__real-coin-drop.wav | Looting coins (gold/platinum collection messages) |
| 327909__ruonvniekerk__dragging-on-floor.wav | Corpse dragging ("[name] drags corpse of [name] along behind") |

## Implementation Patterns

### 1. Basic Trigger Sound
```lua
<script>
sound("filename.wav")
</script>
```

### 2. Conditional Sound
```lua
<script>
if matches[2] == whoami() then
  sound("86324__timbre__smashing-1a.wav")
end
</script>
```

### 3. Limited Sound for Important Events
```lua
<script>
sound("365641__furbyguy__8-bit-alarm.wav", nil, true)
</script>
```

### 4. Sound with Custom Volume
```lua
<script>
sound("105308__kovrov__rumble.wav", 50)  -- 50% volume
</script>
```

### 5. Suppressed Sound Pattern
Used in automated actions to prevent sound spam:
```lua
noSound = true
mud:send("worm " .. target)
-- Next sound will be suppressed
```

## Sound File Naming Convention

Files follow the freesound.org naming pattern:
`[ID]__[username]__[description].wav`

Example: `365641__furbyguy__8-bit-alarm.wav`
- ID: 365641
- User: furbyguy
- Description: 8-bit-alarm

## Debug and Testing

### Debug Output
When sounds play, debug information appears:
```
[sound: filename.wav]
```

### Testing Commands
The package includes commented test commands for various sound files:
```lua
--playSoundFile("\\tmp\\165331__ani-music__tubular-bell-of-death.wav")
--playSoundFile("\\tmp\\209740__yummie__minion-yahoo-2.wav")
--playSoundFile("\\tmp\\274736__sforsman__distort-ring-2.wav")
--playSoundFile("\\tmp\\85568__joelaudio__dragon-roar.wav")
--playSoundFile("\\tmp\\45809__themfish__gas-fire-catch.wav")
--sound("365641__furbyguy__8-bit-alarm.wav")
--sound("105308__kovrov__rumble.wav")
--sound("139025__rj10328__131659-bertrof-game-sound-intro-to-game-80921-justinbw-buttonchime02up-4.wav")
```

### Sound Alias
A help alias provides guidance on sound resources:
```xml
<Alias isActive="yes" isFolder="no">
    <name>sound</name>
    <script>mud:send("GCC LF: suggested sound id#'s and events to play them - https://www.freesound.org/")</script>
    <regex>^sound$</regex>
</Alias>
```
- **Command**: `sound`
- **Output**: Displays information about freesound.org for finding sound effects

## File System Notes

### Legacy Path Reference
Old system path found in mSoundFile:
```
C:/Users/Chris/.config/mudlet/profiles/toril 006/NyyLIB.006/beep.wav
```

### Current Path Structure
- Base: `NyyLIB.homedir`
- Sound directory: `sounds\`
- Full path example: `[homedir]/sounds/filename.wav`

## Best Practices

1. **Use Limited Sounds Sparingly**: Only for critical communications
2. **Test Sound Paths**: Use `soundpath()` to validate files exist
3. **Consider Volume**: Default 100, adjust for less important sounds
4. **Use noSound for Automation**: Prevent sound spam in scripted sequences
5. **Follow Naming Convention**: Use descriptive filenames from freesound.org

## Integration with LuminariGUI

When adapting these techniques for LuminariGUI:

1. **Path Adaptation**: Change from `NyyLIB.homedir .. "sounds\"` to appropriate LuminariGUI paths
2. **Settings Integration**: Map to LuminariGUI's settings system instead of `charData`
3. **Limited Mode**: Consider which events warrant "limited" mode playback
4. **Volume Defaults**: Establish consistent volume levels for different sound categories

## Complete Trigger Reference

### Communication Triggers
- **Gruumsh responds to your petition with** - Plays alert sound (limited)
- **tells you** - Direct tell notification (limited)
- **An ogre shaman from Faang watches you closely** - NPC attention (currently disabled)

### Combat/Death Triggers
- **The world starts spinning, and your ears are ringing!** - Stun effect
- **[Name] has died!** - Group member death (special sound for Lilithelle)
- **Stand Triggers** - Various sprawl/slam/earthquake messages
- **Bash messages** - Recovery from bash
- **Upon being struck, a mirror image of [Name] shatters** - Mirror image destruction
- **You are burned as you hit** - Burn damage

### Status/Buff Triggers
- **You feel yourself growing, in strength and size** - Supple girdle activation
- **Your soul is transported to The Fugue Plane** - Player death
- **Resurrection sound** - Various resurrection messages

### Action Triggers
- **[Name] drags corpse of [Name] along behind** - Corpse dragging
- **Looting coins** - Gold/platinum collection
- **Roller** - Character creation roller alerts (limited)

### Environmental Triggers
- **Dragon sound** - Dragon breath/roar attacks
- **Inferno sound** - Fire effects

## Complete Sound File Reference

All 17 unique sound files used in the system:

1. **165331__ani-music__tubular-bell-of-death.wav** - Death sound
2. **195954_minian89_death-blood-splatter.wav** - Combat death
3. **209740__yummie__minion-yahoo-2.wav** - Special character death
4. **241280__sonictechtonic__gooeybashes.wav** - Bash recovery
5. **274736__sforsman__distort-ring-2.wav** - Stun effect
6. **320181__dland__hint.wav** - Tell notification
7. **327909__ruonvniekerk__dragging-on-floor.wav** - Corpse drag
8. **343462__rocotilos__real-coin-drop.wav** - Coin loot
9. **365641__furbyguy__8-bit-alarm.wav** - Alert/tell (limited)
10. **368014__trngle__burning-match-into-water.wav** - Burn damage
11. **45809__themfish__gas-fire-catch.wav** - Fire/inferno
12. **72127__kizilsungur__sweetalertsound3.wav** - NPC attention
13. **85568__joelaudio__dragon-roar.wav** - Dragon roar
14. **86324__timbre__smashing-1a.wav** - Mirror image (self)
15. **86324__timbre__smashing-1b.wav** - Mirror image (other)
16. **105308__kovrov__rumble.wav** - Buff activation
17. **139025__rj10328__131659-bertrof-game-sound-intro-to-game-80921-justinbw-buttonchime02up-4.wav** - Resurrection