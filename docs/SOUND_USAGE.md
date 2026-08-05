# LuminariGUI Sound System

LuminariGUI has one Mudlet-native sound layer for chat and status alerts. It
uses Mudlet's `playSoundFile({...})` media API, gives every playback a stable
key and the `LuminariGUI` tag, and stops only package-owned sounds during
profile cleanup. No external player or downloaded media is required.

All channels are off by default. Existing `chatSound` preferences migrate into
the new settings automatically, so users who had chat notifications enabled do
not lose that choice.

## Channels

| Command name | Purpose | Bundled default | Volume | Cooldown | Threshold |
|---|---|---|---:|---:|---:|
| `chat` | New YATCO message outside the active channel tab | `audio/chat_sound.mp3` | 100 | 0s | — |
| `health` | Health crosses into the low range | `audio/health_warning.wav` | 75 | 30s | 25% |
| `moves` | Movement crosses into the low range | `audio/movement_warning.wav` | 65 | 30s | 20% |

The two warning cues are bundled as mono, 16-bit, 44.1 kHz PCM WAV files for
portable decoding. Chat keeps the existing MP3 asset.

## Quick start

```text
sound status
sound health on
sound moves on
sound health test
sound moves test
```

`test` always plays the selected channel. It intentionally bypasses the master
switch, channel switch, and cooldown so configuration can be checked before it
is enabled.

## Commands

| Command | Effect |
|---|---|
| `sound` or `sound status` | Show master and per-channel settings |
| `sound help` | Show command help |
| `sound all on\|off` | Change the master switch without losing channel choices |
| `sound chat\|health\|moves on\|off` | Enable or disable one channel |
| `sound <channel> volume <0-100>` | Set channel playback volume |
| `sound <channel> cooldown <0-3600>` | Set minimum seconds between plays |
| `sound health\|moves threshold <1-95>` | Set the low-vitals crossing percentage |
| `sound <channel> file <relative path>` | Select a package/profile-local sound |
| `sound <channel> test` | Force one test playback |
| `sound stop` | Stop sounds tagged as owned by LuminariGUI |

The historical commands remain compatible and now delegate to this layer:

- `dsound` toggles the `chat` channel and plays a test when enabling it.
- `set chat sound on|off`
- `set chat sound volume <0-100>`
- `set chat sound cooldown <0-3600>`
- `set chat sound file <relative path>`
- `set chat sound test`
- bare `set chat sound` safely shows chat status.

## Low-vitals behavior

Health and movement alerts are edge-triggered, not event-triggered:

1. The first MSDP value at or below the threshold plays once.
2. Further low values remain latched and do not spam audio.
3. The alert re-arms only after recovery to the reset percentage.
4. A later downward crossing can play again, subject to its cooldown.

The default health reset is 35%; the movement reset is 30%. If a threshold is
raised through the command, its reset point is kept at least five percentage
points higher. This hysteresis prevents repeated cues around one boundary.

Chat retains YATCO's active-tab suppression: a message in the channel already
being viewed is silent. The `All` tab behavior remains unchanged.

## Files and persistence

Relative files are resolved in this order:

1. `[MudletHomeDir]/LuminariGUI/<file>`
2. `[MudletHomeDir]/<file>`

Absolute paths, URLs, and `..` traversal are rejected. Copy a custom file into
one of those two roots, set its relative path, then run `sound <channel> test`.
A missing or rejected file produces a clear error and never falls back to an
unrelated system beep.

Settings are stored inside the existing `[MudletHomeDir]/GUI.toggles.lua`
table. Master state, enabled channels, files, volumes, cooldowns, priorities,
thresholds, and reset points survive profile reloads. The legacy YATCO sound
fields remain synchronized for third-party scripts that read them.

## Lua API

Extensions can reuse the same ownership and cooldown behavior:

```lua
-- Respects master/channel switches and cooldown.
local played, reason = GUI.Sound.play("chat")

-- Force a configuration test.
GUI.Sound.play("low_health", {force = true})

-- Edge-trigger a configured threshold channel.
GUI.Sound.checkThreshold("low_moves", currentMoves, maximumMoves)

-- Stop only LuminariGUI-tagged sounds.
GUI.Sound.stopAll()
```

Canonical API channel names are `chat`, `low_health`, and `low_moves`.
`health`, `moves`, and `movement` are accepted aliases. `GUI.Sound.play()`
returns `false` with a reason such as `master-disabled`, `channel-disabled`,
`cooldown`, or a file/media error when nothing played.

## Troubleshooting

- Run `sound <channel> test`; this separates file/decoder problems from channel
  enablement and threshold state.
- Run `sound status` to confirm the master switch, channel switch, file,
  volume, cooldown, and threshold.
- Verify the file exists under one of the two supported roots and that its path
  contains no traversal.
- Mudlet 4.22.0's Qt media backend decodes all three bundled assets. Platform
  audio output still depends on the operating system's selected device and
  volume.
- With `GUI.DEBUG = true`, look for `SOUND/LOAD`, `SOUND/PLAY`, or
  `LGUI-ERROR [SOUND/...]` diagnostics.
