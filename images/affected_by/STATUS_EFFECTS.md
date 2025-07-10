# Status Effect Icons Guide

This directory contains 90 status effect icons used by LuminariGUI to visually represent various character conditions, spell effects, and combat modes. Each icon is a PNG file that displays in the GUI when the corresponding effect is active.

## Status Effect Categories

### 🛡️ Defensive Effects
- **Acid-Shielded.png** - Protection from acid damage
- **Cold-Shielded.png** - Protection from cold damage  
- **Fire-Shielded.png** - Protection from fire damage
- **Shadow-Shielded.png** - Protection from shadow/negative energy
- **Globe-of-Invuln.png** - Globe of Invulnerability spell
- **Minor-Globed.png** - Minor Globe of Invulnerability
- **Protect-Elements.png** - Protection from elemental damage
- **Protect-Evil.png** - Protection from evil creatures
- **Protect-Good.png** - Protection from good creatures
- **Spell-Resistant.png** - Spell resistance active
- **Spell-Turning.png** - Spell turning active
- **Warded.png** - General magical protection

### 👁️ Vision and Detection
- **Aware.png** - Heightened awareness
- **Danger-Sense.png** - Danger sense active
- **Dark-Vision.png** - Dark vision ability
- **Detect-Alignment.png** - Detect alignment spell
- **Detect-Invisible.png** - Detect invisible creatures
- **Detect-Magic.png** - Detect magic auras
- **Farsee.png** - Enhanced vision range
- **Infra-Vision.png** - Infrared vision
- **Sense-Life.png** - Sense living creatures
- **True-Sight.png** - True sight ability
- **Ultra-Vision.png** - Enhanced vision capabilities

### ⚔️ Combat Modes & Stances
- **Acrobatic.png** - Acrobatic combat stance
- **Battletide.png** - Battletide spell effect
- **Charging.png** - Charging attack mode
- **Defensive-Casting.png** - Defensive casting stance
- **Dual-wield.png** - Dual wielding combat
- **Flurry-of-Blows.png** - Monk flurry of blows
- **Mode-Expertise.png** - Combat expertise mode
- **Mode-PowerAttack.png** - Power attack mode
- **Mode-RapidShot.png** - Rapid shot mode
- **Mode-Total-Defense.png** - Total defense stance
- **Spellbattle.png** - Spellbattle mode
- **Whirlwind-Attack.png** - Whirlwind attack ability

### 🏃 Movement & Mobility
- **Flying.png** - Flight capability
- **Free-Movement.png** - Freedom of movement
- **Hasted.png** - Haste spell effect
- **Safefall.png** - Safe fall ability
- **Slowed.png** - Slow spell effect
- **Underwater-Breathing.png** - Water breathing
- **Water-Walk.png** - Water walking ability

### 🎭 Concealment & Stealth
- **Blackmantled.png** - Blackmantle spell
- **Blinking.png** - Blink spell effect
- **Blurred.png** - Blur spell effect
- **Displaced.png** - Displacement effect
- **Hiding.png** - Hiding/concealment
- **Incorporeal.png** - Incorporeal form
- **Invisible.png** - Invisibility spell
- **Mirror-Imaged.png** - Mirror image spell
- **Sneaking.png** - Stealth mode
- **Spell-Mantled.png** - Spell mantle effect

### 😵 Debuffs & Negative Effects
- **Blinded.png** - Blindness condition
- **Caged.png** - Trapped or caged
- **Charmed.png** - Charm effect
- **Confused.png** - Confusion spell
- **Cursed.png** - Curse effect
- **Dazed.png** - Dazed condition
- **Deaf.png** - Deafness condition
- **Dimensional-Locked.png** - Dimensional lock
- **Diseased.png** - Disease condition
- **Entangled.png** - Entanglement
- **Faerie-Fired.png** - Faerie fire spell
- **Fatigued.png** - Fatigue condition
- **Fear.png** - Fear effect
- **Feinted.png** - Feinted in combat
- **Flat-footed.png** - Flat-footed condition
- **Grappled.png** - Grappled condition
- **Mage-Flamed.png** - Mage flame effect
- **Nauseated.png** - Nausea condition
- **Paralyzed.png** - Paralysis condition
- **Pinned.png** - Pinned condition
- **Poison.png** - Poison effect
- **Sleep.png** - Sleep spell
- **Stunned.png** - Stunned condition
- **Time-Stopped.png** - Time stop effect
- **Vampiric-Curse.png** - Vampiric curse
- **Vampiric-Touch.png** - Vampiric touch spell

### 🌟 Special Abilities & Buffs
- **Bravery.png** - Courage/bravery effect
- **Counterspell.png** - Counterspell ready
- **Death-Ward.png** - Death ward protection
- **Listen-Mode.png** - Enhanced listening
- **Mind-Blanked.png** - Mind blank spell
- **Refuged.png** - Refuge spell effect
- **Regenerating.png** - Regeneration ability
- **Size-Changed.png** - Size alteration spell
- **Spot-Mode.png** - Enhanced spotting
- **Tower-of-Iron-Will.png** - Mental fortification
- **WildShape.png** - Druid wild shape

## Usage in LuminariGUI

These icons are automatically displayed in the status effects panel when your character has the corresponding condition. The GUI uses MSDP (Mud Server Data Protocol) to receive real-time updates about your character's status and displays the appropriate icons.

### Icon Display Rules
- Icons appear when effects are active
- Icons are removed when effects end
- Multiple icons can be active simultaneously
- Icons are arranged in a grid layout
- Hovering over icons shows effect names (where supported)

## Technical Details

- **Format**: PNG images with transparency
- **Size**: Optimized for GUI display
- **Location**: `images/affected_by/` directory
- **Loading**: Automatically loaded by LuminariGUI on startup
- **Updates**: Real-time via MSDP protocol

## Adding New Icons

To add new status effect icons:
1. Create a PNG image with the same naming convention
2. Place it in the `images/affected_by/` directory
3. Update the GUI code to recognize the new effect
4. Test with the corresponding game effect

## Troubleshooting

If icons are not displaying:
- Verify PNG files are not corrupted
- Check MSDP is enabled: `msdp` command in-game
- Ensure GUI is properly loaded
- Check debug output for missing icon warnings