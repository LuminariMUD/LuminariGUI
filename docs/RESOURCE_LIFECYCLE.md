# Runtime Resource Ownership

LuminariGUI treats every runtime-created anonymous event handler and temporary
timer as an owned resource. The ownership layer is defined in
`theGUI/src/scripts/00_resources.xml` and loads before the mapper and GUI.

This document records the ownership contract, cleanup boundaries, and the
verification baseline for package version `2.0.4.045`.

## Invariants

- Do not call `registerAnonymousEventHandler()` or `tempTimer()` directly from
  package Lua. Use `GUI.registerOwnedHandler()` and `GUI.setOwnedTimer()`.
- Every handler ID belongs to one explicit registry. Re-registering the same
  key removes its previous ID before creating a replacement.
- Every timer has a stable, descriptive name. Scheduling the same name cancels
  its previous timer before creating a replacement.
- A completed one-shot timer removes its ID from `GUI.ownedTimerIds` before it
  calls application code. A callback may therefore safely schedule its own
  successor under the same name.
- Package uninstall removes GUI, mapper, and lifecycle handlers after
  canceling timers. The `sysUninstallPackage` handler removes lifecycle
  handlers last because it owns the cleanup callback that is currently
  running.
- `sysExitEvent` cancels timers and saves preferences, but it does not remove
  handler registrations from a profile that Mudlet is already closing.

## Handler ownership

| Owner | Registry | Count | Events |
|---|---|---:|---|
| Mapper | `map.fileScopeHandlerIds` | 5 | `msdp.ROOM`, `shiftRoom`, `sysConnectionEvent`, `sysProtocolEnabled`, `sysDownloadDone` |
| GUI MSDP updates | `GUI.eventHandlerIds` | 25 | Entries in `GUI.EVENT_HANDLERS` |
| Lifecycle | `GUI.lifecycleHandlerIds` | 6 | `sysLoadEvent`, `sysInstall`, `sysProtocolEnabled`, `sysConnectionEvent`, `sysExitEvent`, `sysUninstallPackage` |
| Package XML | `<eventHandlerList>` | 2 | YATCO start and install hooks |

The runtime baseline is therefore 36 anonymous handlers plus two handlers
owned by Mudlet's imported package XML. `msdp.ROOM` intentionally has two
different callbacks: `map.eventHandler` and `GUI.updateRoom`.

`GUI.unregisterEventHandlers()` removes only keys present in
`GUI.EVENT_HANDLERS`. It must not sweep unrelated or legacy keys from
`GUI.eventHandlerIds`; Mudlet 4.21 can reuse handler IDs during an in-session
package replacement.

## Timer ownership

`GUI.setOwnedTimer(name, delay, callback)` provides replace-before-create
semantics for every temporary timer. `GUI.cancelOwnedTimer(name)` removes one
timer, and `GUI.cancelAllOwnedTimers()` is the profile-exit and uninstall
boundary.

The source audit currently finds 21 owned timer creation sites. Twenty are
one-shot scheduling sites. `yatco.blink` is the one intentional recurring
timer, and each tick schedules exactly one successor. Multiple call sites may
share one name, such as the two mapper-mode controls that both schedule
`buttons.mapRefresh`; the audit number is a source-site count, not the number
of simultaneously live timers.

Dynamic coalescing names are allowed when the key space is bounded by
short-lived call contexts. `GUI.initializeOrRefresh()` uses
`gui.refreshCallPending.<context>` so repeated calls with the same context
collapse into one refresh and completed entries disappear from the registry.

## Cleanup sequence

`GUI.cleanup()` performs profile-exit cleanup:

1. Stop the YATCO blink loop.
2. Cancel every timer in `GUI.ownedTimerIds`.
3. Clear timer-backed coalescing flags.
4. Remove the active temporary ASCII-map line trigger, if present.
5. Save toggle preferences.

`GUI.cleanupPackageResources()` extends that sequence for package uninstall:

1. Unregister the 25 GUI handlers.
2. Unregister the five mapper handlers.
3. Remove the mapper's temporary aliases.
4. Unregister the six lifecycle handlers last.

## Audit commands

The analyzer assembles current source fragments in memory by default, so it
does not depend on an already rebuilt `LuminariGUI.xml`:

```bash
python3 scripts/analyze_handlers.py
python3 scripts/analyze_handlers.py --fail-on-unowned
python3 scripts/analyze_handlers.py --json --fail-on-unowned
python3 scripts/analyze_handlers.py --xml LuminariGUI.xml
```

`--fail-on-unowned` exits 1 if package Lua contains a raw runtime handler or
timer registration outside the ownership manager. XML-owned handler lists are
reported separately and do not count as unowned runtime registrations.

## Verification baseline

Automated lifecycle regressions execute the production Lua through Mudlet API
mocks and assert exact counts after package load, in-session recompilation,
reconnect, `resetProfile()`, ten settled `fix gui` calls, and ten rapid calls.
They also verify timer replacement, recurring-timer bounds, analyzer failure
on an injected raw timer, and complete uninstall cleanup.

The 2026-08-05 Mudlet 4.22.0 runtime check used an isolated portable profile
and a local MSDP server. It confirmed:

- stable counts of 5 mapper + 26 GUI + 6 lifecycle handlers after load,
  reconnect, `resetProfile()`, and repeated refreshes;
- exactly one mapper and one GUI callback for each deliberately shared room,
  protocol, and connection event;
- balanced replacement of 26 registrations and 26 removals for a rapid
  coalesced refresh, and 260/260 across ten settled refreshes;
- no settled one-shot timer IDs and at most one recurring `yatco.blink` ID;
  and
- zero owned timers, GUI handlers, mapper handlers, lifecycle handlers, and
  mapper aliases after actual package uninstall.

The current automated baseline is one GUI handler lower because version
`2.0.4.045` removed the unused `msdp.ALIGNMENT` player-refresh registration.
The live Mudlet check above remains the historical evidence for version
`2.0.4.039`; section 2 of the smoke test now verifies the narrowed report set.

Run the permanent gates with:

```bash
python3 tests/run_tests.py --skip-optional --test lifecycle
python3 tests/run_tests.py --skip-optional
python3 scripts/analyze_handlers.py --fail-on-unowned
python3 theGUI/build.py --diff --fail-on-diff
```
