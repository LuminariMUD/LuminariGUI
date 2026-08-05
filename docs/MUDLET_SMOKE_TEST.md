# Mudlet Runtime Smoke Test

This is the release checklist for LuminariGUI on the current documented Mudlet
release. The automated Lua tests exercise production code with mocks; they do
not prove that Mudlet imported the package, Qt rendered it, Geyser callbacks
survived a reset, physical keys arrived, or the server negotiated MSDP.

The documented target is currently **Mudlet 4.22.0**. Re-read
[`MUDLET_COMPATIBILITY.md`](MUDLET_COMPATIBILITY.md) before each run and update
both documents when the supported release changes.

## Release rule

A release candidate needs a completed real-Mudlet checklist. The optional
`Mudlet / smoke` GitHub job is evidence about Linux Qt startup only and cannot
approve a release. Do not convert a documented upstream Mudlet regression into
a package pass: record it as `UPSTREAM-BLOCKED`, link the matching compatibility
entry, and still test unaffected checklist sections.

Use these result values:

- `PASS`: observed the expected behavior in the supported Mudlet release.
- `FAIL-PACKAGE`: behavior is wrong and does not match a documented upstream
  regression.
- `UPSTREAM-BLOCKED`: behavior matches a linked Mudlet issue and the package
  cannot reasonably correct it.
- `NOT-TESTED`: the setup could not exercise the behavior. This does not count
  as a release pass.

## Prepare the candidate

Start from a clean checkout and a new, disposable Mudlet profile. Do not reuse
a player's credentials or layouts. Record the operating system, display
server/window manager, Mudlet version, package commit, package version, screen
size/scaling, and whether the connection is a local fixture or LuminariMUD.

Run the permanent non-mutating gates first:

```bash
python3 theGUI/build.py --validate
python3 theGUI/build.py --diff --fail-on-diff
python3 tests/run_tests.py --skip-optional
python3 scripts/validate_package.py
python3 scripts/analyze_handlers.py --fail-on-unowned
```

For release-like asset testing, create a local development package from the
already validated XML:

```bash
python3 theGUI/package.py create --dev --skip-build
```

Import that `.mpackage`, not an individual source fragment. In Profile
Preferences, enable MSDP from the Protocols menu before connecting.

## Runtime checklist

Record a result and short evidence note for every numbered section.

### 1. Fresh import and assets

1. Import the candidate into the disposable profile.
2. Confirm there is one LuminariGUI package tree and no import error in the
   error/debug consoles.
3. Confirm the GUI shell, textures, action icons, and chat sound asset resolve
   from the installed `LuminariGUI` package directory.
4. Confirm one mapper view and one ASCII-map view are created, without a blank
   duplicate window.

Failure attribution: missing package items or assets is a package failure.
Qt-only rendering differences belong in section 9, with screenshots.

### 2. Connection and MSDP

1. Connect to an MSDP-capable local fixture or LuminariMUD and confirm Mudlet
   prints the package's protocol-enabled message.
2. Inspect `GUI.MSDP_REPORT_VARS` in the Lua console and confirm the expected
   subscription set is present.
3. Observe live room, health/mana/movement, opponent, group, affect, action,
   and character updates where the test account can produce them.
4. Confirm a room update reaches both `map.eventHandler` and `GUI.updateRoom`
   once each; duplicate output or redraws are a failure.

If nothing updates, first re-check the relocated Mudlet 4.20+ Protocols menu.
The Mudlet 4.21 client-variable rename does not change LuminariGUI's `REPORT`
calls; see the compatibility reference before attributing it.

### 3. Mapper modes and controls

1. Switch between the Mudlet mapper and ASCII map.
2. Exercise legend and mapper control callbacks.
3. Move through several connected rooms and confirm room name, exits, terrain,
   and both map views remain synchronized.
4. Confirm there is no callback error after hovering and clicking labels.

### 4. YATCO and callbacks

1. Confirm YATCO starts once and exposes all configured tabs.
2. Click every chat tab and every tabbed information pane.
3. Produce captured chat in at least two categories; confirm it appears once
   in the correct tab and the unread/blink state clears on selection.
4. Toggle chat sound and verify enabled/disabled behavior without a Lua or
   media-backend error.

An `attempt to call a number value` error after reset or label interaction is
the historical Mudlet callback-registry symptom; it is a package failure on
4.22 unless a new upstream issue is demonstrated.

### 5. Aliases and physical numeric keypad

1. Exercise every package alias from the command line, including GUI toggles,
   `fix gui`, YATCO controls, and mapper-mode controls. Confirm each matching
   alias sends or performs exactly one action.
2. With Num Lock in both relevant states, press the physical numeric keypad
   movement keys. Cover cardinal, diagonal, up/down, and center/look bindings
   present in the package.
3. Exercise every defined Shift/Ctrl/Alt keypad variant.
4. Confirm the main keyboard number row does not accidentally trigger keypad
   movement.

Structural tests cannot prove the distinction between physical keypad and
number-row events. Record the keyboard layout and platform with this section.

### 6. Repeated refresh and reconnect

1. Run `fix gui` ten times rapidly and ten times after each refresh settles.
2. Confirm there is no duplicate chat/output, progressive slowdown, or widget
   duplication.
3. Disconnect and reconnect. Confirm one refresh, one MSDP subscription batch,
   stable maps, and stable callbacks.
4. Compare live handler/timer observations with
   [`RESOURCE_LIFECYCLE.md`](RESOURCE_LIFECYCLE.md): 5 mapper, 26 GUI, and 6
   lifecycle anonymous handlers; at most one recurring `yatco.blink` timer
   after one-shot work settles.

### 7. `resetProfile()`

1. While connected, run `resetProfile()` and confirm `sysLoadEvent` reports a
   reset (`isNewLoad == false`).
2. Confirm the cleared `msdp` table is recreated, both map views return, and
   the full `REPORT` batch is sent without waiting for another protocol event.
3. Hover and click labels, switch tabs, and move rooms after the reset.
4. Confirm handler counts and recurring timers match the pre-reset baseline.

### 8. Package replacement and uninstall

1. Install the preceding supported package version, connect, and then install
   the candidate in the same session using the supported replacement path.
2. Confirm one effective connection/refresh path and no legacy callback fanout.
3. Uninstall the candidate and confirm owned handlers, timers, and mapper
   aliases reach zero.
4. Reinstall once and repeat a minimal connection/tab/map check.

Released Mudlet versions around 4.21/4.22 have had package-uninstall crashes.
If the failure occurs inside Mudlet before LuminariGUI cleanup runs, compare it
with Mudlet issue #9337 and PR #9557 from the compatibility reference and mark
the step `UPSTREAM-BLOCKED`, not `PASS`.

### 9. Qt6/Geyser visual and resize pass

1. Capture full-window screenshots at the baseline size, a narrow size, a
   large size, and the platform's supported scaling factor.
2. Inspect backgrounds, borders, vertical text alignment, gauge text, tab
   outlines, z-order, clipping, and mini-console wrapping.
3. Resize in floating, tiled, and fullscreen states where the window manager
   supports them. Confirm negative-offset containers remain visible.
4. Toggle timestamps and confirm the `sysConsoleSizeChanged` path keeps layout
   and wrapping current.
5. Save and reload every Adjustable.Container layout profile.

Keep this section manual. A headless Xvfb screenshot is useful crash evidence,
but it is not a stable oracle for platform font metrics, QSS rendering, window
manager resize delivery, or the documented mini-console edge regression.

## Evidence record

Store the completed record with the release notes or release issue. Do not
commit profiles, credentials, or raw server logs containing private text.

```text
Date/time (UTC):
Tester:
Commit / package version:
Mudlet version and official build:
OS / architecture / display server / window manager:
Screen size / scale / keyboard layout:
Connection target (non-secret description):

1 Fresh import/assets:              PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
2 Connection/MSDP:                  PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
3 Mapper modes/callbacks:           PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
4 YATCO/callbacks:                  PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
5 Aliases/physical keypad:          PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
6 Refresh/reconnect:                PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
7 resetProfile():                   PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
8 Replacement/uninstall/reinstall:  PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED
9 Qt6/Geyser visual/resize:         PASS | FAIL-PACKAGE | UPSTREAM-BLOCKED | NOT-TESTED

Package failures and reproduction steps:
Upstream-blocked steps and issue links:
Error/debug console excerpt (redacted):
Screenshot/log artifact locations:
Release decision: APPROVE | REJECT
```

## Targeted acceptance records

### 2026-08-05 — QSS and input backlog closeout

This was a focused acceptance pass for checklist sections 5 and 9, not a full
release approval. It used the official Linux x86_64 Mudlet 4.22.0 AppImage
with Qt 6.9.0, an isolated portable profile, Xvfb at 1600×1000, a 1000×700
resize, the US X11 keymap, and a local non-MSDP TCP fixture. Alias/key evidence
came from package 2.0.4.039; the QSS correction was re-imported as 2.0.4.041.

- **Aliases:** `gag chat`, `show self`, `hscroll`, `chaseres`, `fix gui`,
  `debug list`, `debugc`, `dblink`, `set chat sound volume 42`, `dsound`, and
  `fix chat` each matched in Mudlet. `dsound` was run once in each direction.
  No alias command reached the TCP fixture.
- **Keypad:** with Num Lock on, XTEST-delivered Qt keypad events produced
  `southwest`, `south`, `southeast`, `west`, `look`, `east`, `northwest`,
  `north`, `northeast`, `inv`, `scan`, `up`, and `down`, each exactly once.
  With Num Lock off, the four operator keys retained their bindings and the
  nine navigation-mode keys remained unbound, matching the package's declared
  numeric-key bindings. A number-row `1` stayed in the command line and sent
  no movement command.
- **QSS:** the original package logged a parse failure for
  `GUI.tabbedInfoWindow.center`, revealing a missing semicolon. After that fix,
  removing `vertical-align`, and expanding scrollbar backgrounds to explicit
  colors, the client logged no stylesheet parse failure. The action-icon crop
  (130×105), scrollbar crop (25×475), and status/action crop (770×250) each had
  an ImageMagick absolute-error count of zero between the before and after
  1600×1000 screenshots. The 1000×700 resize retained the corrected styles.

The keypad events traversed the real X11 → Qt → Mudlet input path and preserved
the keypad modifier distinction, but were injected with XTEST because the
isolated environment had no attached keyboard. A human physical-keyboard pass
therefore remains part of every release-candidate checklist.

## Optional GitHub Xvfb experiment

The manual-dispatch workflow `.github/workflows/mudlet.yml` downloads the
official Mudlet 4.22.0 Linux AppImage archive, verifies the release checksum,
extracts it without FUSE, validates the package without changing the checkout,
and queues `LuminariGUI.xml` on Mudlet's command line under Xvfb. It passes only
when a visible Mudlet window appears. Its 14-day artifact contains the official
version output, checksum result, Mudlet/Xvfb logs, a display screenshot, and a
short result file.

Run it from the Actions UI or with:

```bash
gh workflow run mudlet.yml --ref master
gh run list --workflow mudlet.yml --limit 1
```

The workflow is intentionally `workflow_dispatch`-only and is not a required
branch-protection check. It proves official-binary integrity, Qt startup, and
command-line package queuing in one Linux/Xvfb environment. It does **not**
create a profile, connect, negotiate MSDP, evaluate Geyser visuals, exercise
callbacks, or simulate a physical keypad. Expanding it past this boundary
requires stable profile provisioning and deterministic local MSDP fixtures;
until then, a green job remains advisory.
