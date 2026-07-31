# Mudlet Compatibility Reference (4.19 → 4.22)

**Last researched:** 2026-07-31
**Current Mudlet release:** 4.22.0 (released 2026-07-06)
**Package target declared in `theGUI/package.py`:** `mudlet_version = "4.21+"` (raised from `4.0+` in v2.0.4.028).

This document records what changed in Mudlet between the 4.19 era and 4.22, filtered to **only the changes that can affect LuminariGUI**. It exists because the package worked on an older Mudlet and began misbehaving after upgrading to 4.22.0.

> **Key insight:** 4.22.0 itself is a small, mapper-focused release. It is almost certainly *not* the cause of breakage. The disruptive changes landed in **4.20** (Qt6 migration, protocol settings moved) and **4.21** (MSDP negotiation, PCRE2, label/callback internals). If you jumped from 4.19-or-earlier straight to 4.22, you absorbed all three releases at once.

---

## Release summary

### Mudlet 4.20.0 — the big one
Large release: ~46 new features, 91 improvements, 142 bug fixes, plus major infrastructure churn.

| Change | Why it matters to LuminariGUI |
|---|---|
| **Built with Qt6** on macOS and Linux (Qt 6.9); Windows 64-bit was already Qt6. All Qt5 code paths removed. | Stylesheet (QSS) parsing, font metrics, and widget rendering all shift. LuminariGUI uses `setStyleSheet` 42× and `CSSMan` 30×. **Highest-impact change.** |
| **Protocol checkboxes consolidated into a dropdown menu** in Profile Preferences ([#7744](https://github.com/Mudlet/Mudlet/pull/7744)). "Allow server to install packages / download media" moved into the Protocols area. | MSDP is enabled *here*. If the setting did not survive the profile upgrade, **the entire package goes dark** — every gauge and box gates on `sysProtocolEnabled`. |
| **Fixed incorrect initialisation of `Host::mEnableMSDP`** ([#7762](https://github.com/Mudlet/Mudlet/pull/7762)) | Reinforces the above: MSDP enablement state was genuinely buggy in this window. |
| **`sysLoadEvent` gained a boolean argument** ([#7726](https://github.com/Mudlet/Mudlet/pull/7726)): `true` on a fresh profile load, `false` after `resetProfile()`. | Handlers now receive an extra argument. LuminariGUI registers `GUI.init`, `GUI.loadToggles`, and `GUI.AdjustableContainers.init` on `sysLoadEvent`. |
| **`sysConsoleSizeChanged` event added** ([#7870](https://github.com/Mudlet/Mudlet/pull/7870)) — fires on resize and on toggling timestamps. | A more reliable resize signal than `sysWindowResize` (see the open bug below). |
| **`installPackage()` now returns the boolean it always should have** ([#7818](https://github.com/Mudlet/Mudlet/pull/7818)) | Only matters if scripts branch on its return value. |
| **Packages now behave the same as modules** ([#7729](https://github.com/Mudlet/Mudlet/pull/7729)) | Changes install/reload semantics. |
| **Fixed: Lua local variable declaration leaking into global** ([#7853](https://github.com/Mudlet/Mudlet/pull/7853)) | Code that accidentally relied on the leak now breaks. |
| **`matches[]` in `temp*Trigger` functions fixed** ([#7624](https://github.com/Mudlet/Mudlet/pull/7624)) | Affects dynamically created triggers. |
| Package exporter made "more intuitive", required fields removed ([#7582](https://github.com/Mudlet/Mudlet/pull/7582)); default icon removed for icon-less packages ([#7671](https://github.com/Mudlet/Mudlet/pull/7671)) | Affects `.mpackage` metadata expectations. |
| Windows 32-bit builds removed entirely | Distribution note only. |
| MSDP: Mudlet now reports its client name/version over MSDP when enabled ([#7605](https://github.com/Mudlet/Mudlet/pull/7605)) | Server-visible; see 4.21 for the naming correction. |

### Mudlet 4.21.0 — stability, MSDP spec alignment, label internals

| Change | Why it matters to LuminariGUI |
|---|---|
| **"Align MSDP negotiation to specs"** ([#8905](https://github.com/Mudlet/Mudlet/pull/8905), merged 2026-02-14) — Mudlet previously sent `CLIENT` and `VERSION`; the [MSDP spec](https://mudhalla.net/tintin/protocols/msdp/) requires **`CLIENT_NAME`** and **`CLIENT_VERSION`**. | ⚠️ **Scope check:** this changes only what *Mudlet reports about itself* to the server. It does **not** change `sendMSDP("REPORT", ...)`, which is what LuminariGUI uses. It only matters if LuminariMUD keys behaviour off the old `CLIENT`/`VERSION` variable names — worth confirming server-side, but it is not a client-side break. |
| **Fixed: regression of `resetProfile()` handling of labels** ([#9255](https://github.com/Mudlet/Mudlet/pull/9255), closing [#9254](https://github.com/Mudlet/Mudlet/issues/9254)) | The bug: after `resetProfile()`, hovering **any label inside a Geyser/Adjustable container** threw `attempt to call a number value`, because freed Lua registry indices were reused. LuminariGUI uses 5 `Adjustable.Container` + 20 `Geyser.Label` and ships its own `GUI.AdjustableContainers.resetProfile`. **Fixed in 4.21** — but any workaround added locally may now be redundant or harmful. |
| **Label highlight changed from an overlay to an outline** | Visual difference on hover states. |
| **Migrated C++ regex engine from PCRE to PCRE2**, with JIT enabled for triggers and aliases | Edge-case differences in trigger pattern behaviour; generally faster. |
| **Fixed text wrapping to use full available column width on resize** | Changes miniconsole/chat wrap behaviour. |
| Fixed `echo()` ignoring newlines after `deleteLine()`; `insertText()` newline regression; `selectCaptureGroup()` selecting wrong capture | Affects YATCO chat routing and any gagging logic. |
| Added `Geyser.TextEdit`, `selectAll()`, `permExactMatchTrigger()`, `getKeyCode()`, lpeg | New capabilities, no break. |
| "Improved memory safety by using smart pointers"; several use-after-free fixes | Underlies the label/callback lifetime changes. |
| Stopped scripted package installs from stealing window focus | Cosmetic. |

### Mudlet 4.22.0 — mapper-focused, low risk
Released 2026-07-06.

- **Added:** a Configure Areas UI ([#9342](https://github.com/Mudlet/Mudlet/pull/9342)) — create/rename/delete map areas without scripting.
- **Improved:** locking stub exits ("No route") via the Set Exits GUI; map room name label colour handling.
- **Fixed:** clipboard retaining HTML after Copy HTML; **enable/disable only affecting some same-named items on Windows** ([#9366](https://github.com/Mudlet/Mudlet/pull/9366)); null-stopwatch guard on profile save; map labels no longer editable in view-only mode; toolbar focus stealing.

The Windows same-named-items fix is the only entry with plausible relevance — LuminariGUI has many similarly-named triggers/aliases across groups.

---

## Known open Mudlet bugs relevant to this package

These are **unfixed upstream** as of 4.22.0. If symptoms match, the fix is a workaround here, not a code error.

| Issue | Status | Relevance |
|---|---|---|
| [#9262 — `sysWindowResize` events only triggering sometimes](https://github.com/Mudlet/Mudlet/issues/9262) | Open (2026-05-09) | Reported on tiling window managers: the main window stops emitting resize events when tiled (works when fullscreen/floating); user windows still fire. Result: **Geyser never repositions**, negative-offset containers vanish, word-wrap assumptions go stale. Consider `sysConsoleSizeChanged` as a supplementary signal. |
| [#8856 — Miniconsole adds extra characters/columns at screen edge](https://github.com/Mudlet/Mudlet/issues/8856) | Open (2026-02-01) | Regression vs 4.19.1. Content past the defined width becomes scrollable into empty space. **YATCO uses 7 `Geyser.MiniConsole`s** — directly in scope. |
| [#9446 — `setFontSize` affects styling on `hecho`'d labels](https://github.com/Mudlet/Mudlet/issues/9446) | Open (2026-07-15) | Relevant to any label that mixes font sizing with coloured echo. |
| [#9341 — main console vertical scrollbar invisible on Windows (4.21.0)](https://github.com/Mudlet/Mudlet/issues/9341) | Open | Qt 6.9 styling artifact; cosmetic. |

---

## Audit findings — LuminariGUI-specific

Concrete issues found in this codebase. **All were fixed in v2.0.4.028 (2026-07-31)** — see `docs/CHANGELOG.md`. They are kept here with their original diagnosis, because the reasoning is what makes the fixes reviewable.

### 0. Event handler leak + duplicate registrations — *found during the fix pass, most severe*

`GUI.registerEventHandlers()` is called from both `GUI.init()` and `GUI.initializeOrRefresh()` but never removed handlers it had previously registered. Measured against a mock Mudlet API using the real function:

| Calls | Live handlers (before fix) | After fix |
|---|---|---|
| 1 | 36 | 30 |
| 2 | 68 | 30 |
| 10 | **324** | 30 |

So after a handful of reconnects/refreshes, one MSDP update fanned out to ~10 duplicate handlers — duplicate `REPORT` storms, redundant redraws, and steadily growing latency. This is the most likely explanation for "it works at first but degrades."

Separately, six event→handler pairs were registered **twice** — once at file scope in `00_msdpmapper.xml`, once again in the GUI tables — so `map.eventHandler` processed every room change twice even on a clean start.

**Fixed:** the function now kills only the GUI-table handlers it owns before re-registering (verifiably idempotent), and the duplicate table entries were removed in favour of the file-scope registrations. Limiting cleanup to owned events also preserves file-scope handler IDs reused by Mudlet during an in-place upgrade.

### 1. Legacy string-name callbacks with arguments — *high priority*
```lua
theGUI/src/scripts/03_yatco.xml:187  demonnic.chat.tabs[tab]:setClickCallback("demonnicChatSwitch", tab)
theGUI/src/scripts/01_gui.xml:900    GUI.tabbedInfoWindow[v .. "tab"]:setClickCallback("GUI.tabbedInfoWindow.click", v)
theGUI/src/scripts/01_gui.xml:1640   GUI.buttonWindow.Legendbutton:setClickCallback("GUI.buttonWindow.legendClick")
theGUI/src/scripts/01_gui.xml:1642   GUI.buttonWindow.Mapbutton:setClickCallback("GUI.buttonWindow.mapClick")
```
Passing a **function name as a string plus trailing arguments** is the legacy Geyser form. This is exactly the surface touched by the label-callback registry lifetime work in 4.20/4.21 ([#9254](https://github.com/Mudlet/Mudlet/issues/9254) / [#9255](https://github.com/Mudlet/Mudlet/pull/9255)). **Fixed:** all four sites now use the closure form below. If chat tab switching or the info-window tabs still fail to respond to clicks, that points at the upstream label-callback bug rather than this code.
```lua
tab:setClickCallback(function() demonnicChatSwitch(tab) end)
```

### 2. `box-shadow` in stylesheets — *will never work*
`box-shadow` appears in the GUI stylesheets. **Qt's stylesheet engine has never supported `box-shadow`** — it is not part of QSS. It is silently ignored, but it is dead code and — under Qt6's stricter parsing — an invalid declaration risks the surrounding rule being dropped.

**Fixed:** 8 `box-shadow` and 1 `text-shadow` declarations removed from stylesheets. The `text-shadow` uses inside `echo()` HTML were deliberately left alone: that is Qt's rich-text engine, a different parser from QSS. `background` (shorthand) and `vertical-align` remain in use and have limited QSS support — worth re-verifying visually.

### 3. `config.lua` `dependencies` type mismatch
`theGUI/package.py:233` emits:
```lua
dependencies = {}
```
Mudlet's own package exporter (`src/dlgPackageExporter.cpp`, `writeConfigFile`) writes `dependencies` as a **comma-separated string**, not a Lua table. The full field set Mudlet writes is:

`mpackage`, `author`, `icon`, `title`, `description`, `version`, `helpURL`, `dependencies`, `created`

`package.py` additionally emitted a non-standard `modified` field and omitted `icon` and `helpURL`.

**Fixed:** `dependencies` is now a comma-separated string, `helpURL` added, `modified` removed. `icon` is still omitted deliberately — no icon asset exists in the repo, and since Mudlet 4.20 an icon-less package simply gets no icon, whereas naming a missing file would be worse. Adding a 512x512 icon remains an open improvement.

### 4. Stale `mudlet_version = "4.0+"`
`theGUI/package.py` claimed 4.0+. Given Qt6 rendering, the 4.21 label fixes, and the event-signature changes, the realistic floor is much higher.

**Fixed:** raised to `4.21+` — the first release where Qt6 is universal *and* the `resetProfile()` label regression is fixed. This is a judgement call; adjust if you need to support older clients.

### 5. `sysLoadEvent` handlers ignore the new boolean
`GUI.loadToggles()` (`01_gui.xml:189`), `GUI.init()` (`01_gui.xml:2089`), and `GUI.AdjustableContainers.init()` (`01_gui.xml:2785`) take no parameters. Since 4.20 they receive `(event, isNewLoad)`. Ignoring it meant the package **could not distinguish a fresh profile load from a `resetProfile()`**.

This turned out to matter: after `resetProfile()` the connection is usually still up and MSDP was already negotiated, so `sysProtocolEnabled` does **not** fire again — the GUI never re-sent its `REPORT` subscriptions and sat empty.

**Fixed:** `sysLoadEvent` now reads the boolean and, on `false` (post-reset), calls the exported `map.initialize()` to recreate both map views, then calls `GUI.requestMSDPReports()` and refreshes.

---

## Triage checklist — "the GUI broke after updating"

Work top-down; ordered by likelihood.

1. **Is MSDP actually still enabled?**
   Profile Preferences → Protocols **dropdown** (it is no longer a checkbox list). This alone explains a totally dead GUI. Confirm with:
   ```lua
   lua getConfig and getConfig("enableMSDP")
   ```
   and watch for `MSDP enabled!` printing from `map.onProtocolEnabled`.
2. **Does `sysProtocolEnabled` fire at all?** If not, nothing downstream initialises.
3. **Check the error console** (the red one) for `attempt to call a number value` on label hover/click → callback-registry issue (finding #1).
4. **Do clicks on chat tabs work?** → finding #1.
5. **Are backgrounds/textures missing?** → Qt6 QSS. Verify image paths resolve and that rules parse.
6. **Does the layout fail to follow window resizes?** → upstream [#9262](https://github.com/Mudlet/Mudlet/issues/9262); try fullscreen/floating to confirm, consider `sysConsoleSizeChanged`.
7. **Chat text wrapping/scroll oddities?** → upstream [#8856](https://github.com/Mudlet/Mudlet/issues/8856) plus the 4.21 wrap-width change.
8. **Windows only, some triggers/aliases not enabling?** → fixed in 4.22 ([#9366](https://github.com/Mudlet/Mudlet/pull/9366)); ensure the user is truly on 4.22.0.

Useful during triage:
```lua
lua getMudletVersion("string")   -- confirm the running version
lua getOS()                      -- 4.20+ includes processor/compilation details
```

---

## Sources

- [4.20 – a Mudlet release for 2026](https://www.mudlet.org/2026/02/4-20-a-mudlet-release-for-2026/)
- [Mudlet-4.20.0 release post](https://www.mudlet.org/2026/03/mudlet-4-20-0/)
- [Mudlet 4.21.0 release notes](https://github.com/Mudlet/Mudlet/releases/tag/Mudlet-4.21.0)
- [Mudlet releases index](https://github.com/Mudlet/Mudlet/releases)
- [MSDP protocol specification (TinTin++)](https://mudhalla.net/tintin/protocols/msdp/)
- [Manual:Geyser](https://wiki.mudlet.org/w/manual:geyser) · [Geyser.Label API](https://www.mudlet.org/geyser/files/geyser/Geyser.Label.html) · [Geyser.StyleSheet API](https://www.mudlet.org/geyser/files/geyser/Geyser.StyleSheet.html)
- Mudlet source: `src/dlgPackageExporter.cpp` (`writeConfigFile`) for authoritative `config.lua` fields

## Maintenance

Re-check this document on each Mudlet minor release. The fastest refresh:
```bash
gh api repos/Mudlet/Mudlet/releases/tags/Mudlet-<version> --jq '.body'
```
