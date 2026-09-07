# Preserve output spacing and capture complete ASCII maps

Date: 2026-09-07

Status: Implemented and verified on `fix/output-spacing-ascii-map`; this is not
a release approval.

GUI baseline: `ab33a52`, package `2.0.4.045`.

## Outcome

Both reported problems are reproducible. The GUI deletes every empty line,
independently of the server's compact preference. Its temporary map trigger
also starts one row late in Mudlet 4.22.0, leaving the first row in the main
console and copying only eight rows of a nine-row room map. The fixed capture
length causes a separate truncation problem for taller maps.

The exact reported room was checked on the user-provided local server,
`127.0.0.1:4100`: room `145202`, immediately south of `145201`. The server
sent the complete map, including `    [.]-[|]-[.]` on its first row. Replaying
that captured output through the unchanged production triggers in native
Mudlet 4.22.0 reproduced the reported leak and missing row.

The implementation below now replaces both faulty trigger paths. The initial
investigation itself was read-only; subsequent progress entries distinguish
the source, generated package, tests, and documentation changed for the fix.

## Implementation progress

- 2026-09-07: Scope review retained the boundary parser, recovery guard,
  lifecycle cleanup, measured sizing, regression coverage, and native-client
  checks because each protects a reproduced defect or an explicit failure
  case. The implementation uses the existing permanent trigger tree as the
  single line dispatcher and a focused GUI parser script; a second event or
  handler abstraction was removed from the design as unnecessary.
- 2026-09-07: Removed the unconditional blank-line gag and both dynamic map
  triggers. Added one permanent logical-line dispatcher plus the focused
  `GUI.AsciiMapCapture` boundary parser. It validates room/wilderness rows,
  preserves ANSI formatting and exact whitespace, measures completed maps,
  uses 64-row/256-column/131072-byte guards, and owns a five-second inactivity
  timer. Failed transfers and malformed blocks reset before leaving the current
  line readable.
- 2026-09-07: Connected capture reset to GUI refresh, reconnect, profile reset,
  package reload, cleanup, and uninstall paths, including retirement of a
  legacy `map.maplineTrig`. The resource audit now reports 36 owned anonymous
  handlers, 22 owned timer creation sites, two package-XML handlers, and zero
  unowned handlers or timers.
- 2026-09-07: Added and registered eight production-source regression groups.
  They cover normal spacing, the exact `145202` fixture with formatting, room
  heights 3/9/11/13/25, true blank rows, a 21-row wilderness map, multiple and
  nested blocks, mismatches/timeouts/safety limits, destination failures, next-
  map recovery, and lifecycle cleanup. Existing lifecycle coverage now resets
  an active capture and owned timeout during cleanup/uninstall.
- 2026-09-07: Production-trigger native replays pass on official Mudlet 4.21.0
  and 4.22.0 builds and on a version-recorded 5.0.1 comparison. A complete
  generated 2.0.4.046 profile also passed over Mudlet 4.22.0's actual Telnet
  path against the local server: both compact settings captured all nine
  `145202` rows with no map leakage, while compact-off preserved the additional
  server blank line. The character was independently verified back in room
  `1204` with GUI off, compact off, automap on, brief off, and fully logged out.
- 2026-09-07: Final gates passed: build validation, generated-output parity,
  all nine suites supported by the installed tools, standalone package
  validation, handler/timer ownership analysis, and whitespace/error checking.
  `luacheck` was not installed, so the documented `--skip-optional` path ran all
  available suites with `lua` and `luac`; the optional quality suite remains a
  hosted-CI check.

## Evidence and reproduction

### Setup and limits

- Read `docs/MUDLET_COMPATIBILITY.md` before diagnosis. Its documented target
  is 4.22.0; that is the primary reproduction version, not a claim about the
  newest upstream release.
- `python3 theGUI/build.py --diff --fail-on-diff` passed, establishing that
  the checked-in package matches the source fragments.
- Used the official Linux Mudlet 4.22.0 AppImage under Xvfb, with a disposable
  portable profile. The archive's SHA-256 matched the repository CI pin:
  `8f10a78ab918d4b46b1f842c1ca7522b9c26aa8200f657bd8fd5ccba8a7c9040`.
- Imported `theGUI/src/triggers/01_gui.xml` unchanged into the isolated
  profile. Matching, temporary-trigger scheduling, selection, copying,
  deletion, and the destination miniconsole were real Mudlet operations.
  GUI visibility and font-sizing dependencies were stubbed to isolate text
  capture. These results establish a capture defect, not full-layout QA.
- Captured live Telnet text separately, with GUI mode both off and on and
  compact mode both off and on. Replayed the ANSI-bearing text with
  `feedTriggers()` after normalizing CRLF to LF. Direct `feedTriggers()` is
  not the Telnet decoder: feeding CRLF directly introduced artificial empty
  lines in an initial trial; those results were excluded.
- Read main-console and miniconsole buffers with `getLines()` and recorded
  every map-row callback. A complete block and a replay split at each newline
  produced the same first-row failure. A full-package live-Mudlet session was
  subsequently completed, and the native line-split replay and live Telnet
  result agreed. Deliberate transport fragment boundaries were not observable;
  the package parser receives Mudlet's completed logical lines and no longer
  owns byte-stream assembly.
- A comparison run reported Mudlet 5.0.1 and captured all nine rows. The
  disposable runtime's automatic updater had changed the executable between
  runs. Its result was kept separately; automatic downloads were then
  disabled, the verified 4.22.0 image re-extracted, and the live captures
  replayed again with `getMudletVersion("string")` confirming 4.22.0.
- Restored the local test character to room `1204` and its original
  preferences: GUI mode off, compact off, automap on, brief off. Verified
  those settings and completed character and account logout. Authentication
  data is excluded from this document and the replay fixtures.

The user's installed Mudlet version was not available to the automated test.
The supported 4.21/4.22 builds and a newer 5.0.1 comparison now agree, because
the implementation no longer creates a timing-sensitive trigger mid-stream.
The supplied server checkout was at `2fa02cca6`;
the running listener used a binary under its `bin/releases/` directory, so
checkout identity alone is not proof of the running binary's source revision.
The live output independently confirms the relevant map framing and spacing.

### Observed results

Counts below refer to actual map rows, excluding the extra leading newline
that the existing room-map trigger adds to its destination window.

| Input / control | Mudlet 4.22.0 result |
|---|---|
| `A`, blank, `   indented   words`, blank, `B`; blank gag enabled | Both empty lines removed; indentation and spaces between words preserved. |
| Same input; blank gag disabled | Both empty lines and all spaces preserved. |
| Live move `145201 -> 145202`, GUI mode on, compact off | Server sent 9 rows; GUI copied rows 2-9 and left row 1 in the main console. |
| Same live output; blank gag disabled | Still only 8 map rows copied; both non-map blank lines survived instead of zero. |
| Live `look` in `145202`, compact on | Still only 8 map rows copied. With blank gag disabled, one non-map blank line remained, versus two with compact off. |
| Live map for room `145201` | First row was 19 spaces; it remained in the main console. Only 8 rows reached the map window. |
| Synthetic 13-row room map | Copied rows 2-12; row 1, row 13, and `</ROOM_MAP>` remained in the main console. |
| Synthetic 21-row wilderness map | Copied rows 2-21; row 1 remained in the main console. |

The 5.0.1 comparison copied all nine live room-map rows, while its blank-line
gag still removed the non-map empty lines. The 13-row room-map fixture still
exceeded the fixed capture length. Changing the client version therefore
does not resolve the complete scope of these issues.

### Exact room-map fixture

This is the color-stripped map sent by the local server for room `145202`,
represented as a JSON array so trailing spaces are explicit. Leading spaces
and empty-looking rows are map data. The first row has four leading and four
trailing spaces; its text width is 19 characters.

```json
[
  "<ROOM_MAP>",
  "    [.]-[|]-[.]    ",
  "         |         ",
  "    [.]-[C]-[.] [.]",
  "         |       | ",
  "    [.]-[&]-[.] [Y]",
  "         |       | ",
  "    [.]-[C]-[,]-[Y]",
  "         |   |     ",
  "[-]-[-]-[,]-[,]-[.]",
  "</ROOM_MAP>"
]
```

For the same local world, room `145201` begins with **two rows of 19 spaces**
before the visible `[.]-[|]-[.]` row. Losing its first row is much less
noticeable. That provides a concrete explanation for the apparent
intermittency without requiring packet loss or a server omission.

To repeat the live route with a staff test character, record its current
room/preferences first, then use `toggle automap on`, `toggle brief off`,
`toggle compact off`, `toggle guimode on`, `goto 145201`, `south`, and `look`.
Compare the raw stream with the GUI's main and ASCII-map buffers. Repeat with
compact on, and restore the original room/preferences afterward.

## Causes

### 1. An unconditional blank-line gag overrides the server's spacing

In [the GUI triggers](../../theGUI/src/triggers/01_gui.xml), the active
`Gag blank lines` trigger at lines 178-197 matches `^$` and immediately calls
`deleteLine()`. It has no compact-mode check, user preference, or map-capture
condition. It removes blank lines from descriptions, menus, and prompt
separation throughout the main console.

The server explicitly adds a CRLF when compact mode is off in
`Luminari-Source/src/comm.c:3747-3753`. The GUI subsequently removes the
resulting empty line, explaining why turning compact off appears ineffective.

The evidence does **not** show removal of ordinary spaces within lines.
There is also a deliberate server-side formatting difference to control for:
`src/act.informative.c:1618-1634` sends tagged maps plus the original room
description in GUI mode, but calls `str_and_map()` otherwise.
`src/asciimap.c:704-708` wraps/reformats the description for a side-by-side
map. A generic Telnet comparison with different GUI/automap settings is
therefore not expected to have identical horizontal layout.

### 2. Map capture depends on version-sensitive temporary-trigger timing

The same GUI trigger fragment creates:

```lua
-- Capture Wilderness Map, line 29
map.maplineTrig = tempLineTrigger(1, 23, [[onMapLine()]])
-- Capture Room Map, line 114
map.maplineTrig = tempLineTrigger(1, 11, [[onRoomMapLine()]])
```

On the verified 4.22.0 runtime, a line trigger created inside the opening
marker's callback with `from = 1` skips the first following row. A separate
three-line engine probe confirmed the scheduling difference:

| Trigger created while processing `START`, followed by `FIRST`, `SECOND` | 4.22.0 callback sees | 5.0.1 callback sees |
|---|---|---|
| `tempLineTrigger(1, 1, callback)` | `SECOND` | `FIRST` |
| `tempLineTrigger(0, 1, callback)` | `FIRST` | `START` |

The [tagged trigger dispatcher source](https://github.com/Mudlet/Mudlet/blob/Mudlet-4.22.0/src/TriggerUnit.cpp#L284)
iterates a snapshot of the trigger list. A newly created temporary trigger
does not see the opening-marker line. The
[line-trigger matcher](https://github.com/Mudlet/Mudlet/blob/Mudlet-4.22.0/src/TTrigger.cpp#L910)
decrements its start counter before checking for a value below zero. Together
these explain the measured delay. This differs from the
[manual's documented next-line behavior for `from = 1`](https://wiki.mudlet.org/w/Manual:Lua_Functions#tempLineTrigger).
Runtime evidence takes precedence for this diagnosis.

Do not implement a universal `1 -> 0` replacement: the comparison run shows
that it can capture the opening marker on another client version. The fix
should remove this timing dependency.

### 3. Fixed row counts and incomplete boundaries compound the capture bug

The server supplies explicit `<ROOM_MAP>` / `</ROOM_MAP>` and
`<WILDERNESS_MAP>` / `</WILDERNESS_MAP>` boundaries. See
`src/act.informative.c:1622-1628` and
`src/wilderness/wilderness.c:1630-1639,1653-1662`.

Room height is `2 * CONFIG_MINIMAP_SIZE + 1`, from
`src/asciimap.c:500-520`. The checkout configuration has size 4, giving the
nine rows observed live; the configuration editor permits sizes 1-12
(`src/olc/cedit.c:3412`), giving 3-25 rows. A fixed 11-callback trigger can
expire before a valid map ends and never process its closing marker.

Related paths to cover in the same fix:

- Both parsers reject `line == ""` before considering it as a map row,
  printing a warning into the main console. Space-only rows pass that check,
  but truly empty rows do not. Preserve both deliberately.
- Both capture starts overwrite the shared `map.maplineTrig` without first
  canceling an existing capture. Overlapping/interrupted blocks can lose
  ownership of the previous trigger. This is a code-path risk, not a claim
  that it caused the observed first-row loss.
- The success path can delete a row even when `map.minimap` is unavailable
  and no append took place. A destination failure must not discard content.
- Font sizing assumes 20 columns by 11 rows for room maps in
  `theGUI/src/scripts/00_msdpmapper.xml:294-305`. Removing the capture limit
  also requires sizing the destination for the actual completed map.

## Implementation plan

### Step 1: Preserve ordinary server spacing

Remove the unconditional `Gag blank lines` trigger from
`theGUI/src/triggers/01_gui.xml`. Preserve empty and whitespace-only lines
outside map capture by default. Let the server's compact preference control
prompt spacing. No new client compact setting is needed for this fix.

Verify that intentionally relocated chat still follows the existing chat-gag
preference and that normal room text, menus, indentation, and prompt spacing
survive. Map-specific blank rows must be handled by the map parser itself.

### Step 2: Use one permanent parser with explicit map boundaries

Replace the two start-trigger bodies and their dynamically created line
triggers with a single permanent line dispatcher that is present before
incoming output is processed. Verify its pattern fires once for every
logical line, including an empty line, in real Mudlet. Put the small
namespaced parser in a focused child such as
`theGUI/src/scripts/gui/37_ascii_map_capture.xml`, included explicitly by
`theGUI/src/scripts/01_gui.xml` before boot/lifecycle scripts.

The parser should implement these transitions:

| State / input | Required action |
|---|---|
| Idle / ordinary line | Leave the line untouched. |
| Opening room or wilderness marker | End any old capture, validate the destination, set the map kind, clear the destination once, and consume the marker when capture is available. |
| Capturing / valid map row, including blanks | Copy formatting and the complete row to the miniconsole; delete the main-console row only after successful transfer. Track actual row count and visible width. |
| Capturing / matching closing marker | Consume the marker, finish the map, clear capture state, and cancel its timeout. |
| Capturing / another opening marker | Cancel the old capture and start the new block exactly once. |
| Capturing / unexpected text, mismatched end, timeout, or safety limit | Cancel capture before consuming unrelated text; leave that text readable. |

Use the closing marker to determine completion. Row/byte limits and an
inactivity timer are recovery guards, not map-height assumptions. Size those
guards above supported server output; test delayed delivery before choosing
the timeout. Validate room and wilderness row shapes separately, including
their permitted symbols and blank rows, so a missing end marker cannot move
an ordinary room description or prompt into the map window.

Retain ANSI colors through native selection/copy/append operations. Preserve
leading/trailing spaces and blank rows. Account explicitly for any deliberate
display padding; avoid adding an extra data row at the top. If the destination
is unavailable or transfer fails, keep the incoming map readable in the main
console and reset capture safely.

### Step 3: Complete sizing, cleanup, and upgrade behavior

- Fit the map using measured visible width and row count. Verify first and
  last rows remain visible when resizing the ASCII window and when displaying
  supported taller maps. Preserve room/wilderness map-mode controls.
- Replace legacy `map.maplineTrig` cleanup with one namespaced capture-reset
  function. Cancel a retained legacy ID during migration. Reset state on
  reconnect, profile reset, GUI refresh, package replacement, and uninstall.
- Integrate with the existing lifecycle registries and
  `GUI.cleanup()` in `gui/01_preferences.xml:158-163`. Any recovery timer must
  use `GUI.setOwnedTimer()` and a stable name. Add no untracked handlers or
  raw runtime `tempTimer()` calls.
- Remove obsolete global `onMapLine()` / `onRoomMapLine()` callbacks and old
  start triggers so there is only one owner of each incoming map block.

### Step 4: Add regression coverage and verify in real Mudlet

Add a source-linked capture suite, for example
`tests/test_output_capture.py`, and register it with `tests/run_tests.py`.
Keep parser-unit assertions separate from real engine-scheduling checks;
calling a Lua callback directly cannot prove which incoming row invokes it.

Required acceptance cases:

- The exact nine-row `145202` fixture appears completely in the ASCII
  miniconsole, once and in order. No marker or ASCII-map row remains in the
  main console; movement, description, exits, and prompt remain readable.
- Room `145201` retains both initial space-only rows inside the map. Test
  truly empty first/interior/final rows as well.
- Cover room heights 3, 9, 11, 13, and 25 and a 21-row wilderness map. First
  and last rows must survive and the closing marker must always end capture.
- Repeat with compact off/on, GUI mode off/on, automap off/on, brief off/on,
  both map-view modes, chat gag off/on, ANSI colors, and a narrow window.
  Compare ordinary output against the same server settings and width.
- Compare normalized non-map output with the raw fixture: empty-line count,
  indentation, repeated spaces, and prompt separation must match, accounting
  only for explicitly relocated chat. Do not broadly trim whitespace in the
  test oracle.
- Test multiple maps in one input batch, newline-separated delivery,
  arbitrary TCP splits (including within markers and CRLF), blank bursts,
  and delayed map rows. Network tests must use Mudlet's actual Telnet path.
- Test missing/mismatched end markers, consecutive starts, missing widgets,
  append failures, and oversized blocks. Ordinary text after an aborted
  capture must survive and the next valid map must recover.
- Repeat refresh/reconnect/reset/replacement/uninstall while capture is
  active. No stale trigger, timer, duplicate row, or active capture may
  survive its cleanup boundary.
- Run native integration checks on supported 4.21 and 4.22, plus the user's
  actual version. Repeat the 5.0.1 comparison if it is in the support matrix.
  Record the runtime version inside each test result and disable automatic
  updates in disposable profiles to keep comparisons attributable.

### Step 5: Build and hand off the implemented fix

After source changes and focused tests are ready, validate and build once,
then run the repository gates:

```bash
python3 theGUI/build.py --validate
python3 theGUI/build.py
python3 theGUI/build.py --diff --fail-on-diff
python3 tests/run_tests.py --skip-optional
python3 scripts/validate_package.py
python3 scripts/analyze_handlers.py --fail-on-unowned
```

Review the source fragments, manifest, generated XML, archive, and tests
together. Add the spacing and map-boundary cases to
`docs/MUDLET_SMOKE_TEST.md` and record the client timing finding in
`docs/MUDLET_COMPATIBILITY.md`. A release still requires that manual smoke
checklist; this investigation does not constitute release approval.

## Completion criteria

The fix is complete when matching server configurations produce matching
non-map whitespace; every valid tagged map is transferred completely and
exactly once; no map data leaks into the main console during successful
capture; failure recovery preserves ordinary text; and these behaviors hold
across supported client versions and lifecycle transitions.

Investigation artifacts are available locally under
`/tmp/luminari-output-investigation.CXgbf8/`: `prepare_replay.py`, `replay.lua`,
`live-capture.json`, and version-labelled `results-4.22.0.json` /
`results-5.0.1.json`. That temporary directory is not a durable test dependency;
the implementation must check in sanitized fixtures and its regression suite.
