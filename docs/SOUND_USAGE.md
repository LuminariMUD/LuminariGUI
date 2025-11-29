# LuminariGUI Sound System

This document describes the sound configuration and usage in LuminariGUI. Currently, the sound system is primarily focused on chat notifications.

## Chat Sound Notifications

The chat system (YATCO) includes built-in support for audio notifications when messages are received in non-active tabs.

### Configuration Commands

You can configure chat sounds using the `set chat sound` aliases:

| Command | Description |
|---------|-------------|
| `set chat sound on` | Enable sound notifications for all channels |
| `set chat sound off` | Disable sound notifications |
| `set chat sound volume <0-100>` | Set the playback volume (Default: 100) |
| `set chat sound file <filename>` | Set the sound file to play (Default: `audio/chat_sound.mp3`) |
| `set chat sound cooldown <seconds>` | Set minimum time between sounds (Default: 0) |
| `set chat sound test` | Play the current sound to test settings |

### File Locations

The system looks for sound files in the following locations (in order):
1. `[MudletHomeDir]/LuminariGUI/[soundFile]`
2. `[MudletHomeDir]/[soundFile]`

The default file is `audio/chat_sound.mp3`, which corresponds to `[MudletHomeDir]/LuminariGUI/audio/chat_sound.mp3` after standard installation.

### Logic

- Sounds are played when a message arrives in a chat tab.
- **Active Tab Silence**: If you are currently viewing the tab receiving the message, the sound is suppressed (to avoid annoyance while chatting).
- **Cooldown**: You can set a cooldown to prevent spam if multiple messages arrive quickly.
