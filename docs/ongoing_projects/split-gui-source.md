# Split the Main GUI Source Fragment

- **Status:** Implemented; automated validation passes, manual Mudlet validation pending
- **Created:** 2026-07-31
- **Scope:** `theGUI/src/scripts/01_gui.xml` and the build/test support needed
  to split it safely

## Goal

Replace the 3,146-line `theGUI/src/scripts/01_gui.xml` source fragment with a
small wrapper and a set of focused GUI fragments that are easier to navigate,
review, test, and maintain.

Mudlet must still receive one assembled `LuminariGUI.xml` package. This project
changes the development sources and their assembly; it does not change that
distribution model.

## Pre-Migration State

`01_gui.xml` was physically monolithic but already contained useful logical
boundaries:

- One outer `GUI` `ScriptGroup`.
- A nested `CSSman` group.
- A nested `GUI` group with a group-level bootstrap script.
- Nineteen individual Mudlet `Script` nodes.
- Two especially large Lua chunks:
  - `MSDP`: approximately 374 Lua lines.
  - `Config`: approximately 616 Lua lines.

Before this project, the source-to-build system only assembled manifest
fragments at the `ScriptPackage` level. It could not insert independently
maintained fragments inside the existing nested GUI groups. Consequently, the
logical Mudlet scripts remained bundled in one source file.

Baseline checks as of 2026-07-31:

```text
python3 theGUI/build.py --validate                 PASS
python3 theGUI/build.py --diff --fail-on-diff      PASS (no drift)
python3 tests/run_tests.py --skip-optional \
  --test lifecycle --quiet                         PASS
```

## Design Decision

Use a small composite wrapper for the existing GUI `ScriptGroup` and explicitly
include ordered child fragments from `theGUI/src/scripts/gui/` during the
build.

The first migration must be structural only:

- Preserve the current final XML hierarchy.
- Preserve script names and order.
- Preserve group-level script contents.
- Preserve Lua code exactly.
- Preserve file-scope execution and handler-registration order.
- Produce no change in the assembled `LuminariGUI.xml`.

This is preferred over listing every GUI script directly in `build.yaml`, which
would flatten or reparent the Mudlet package tree. It is also preferred over
putting unmatched opening and closing XML tags in separate files, because every
source fragment should remain independently valid XML.

## Implemented Source Layout

```text
theGUI/src/scripts/
├── 01_gui.xml                         # Small composite wrapper/index
└── gui/
    ├── 00_cssman.xml                  # CSSMan subgroup
    ├── 01_preferences.xml             # Toggles, persistence, cleanup
    ├── 10_create_background.xml        # Main background
    ├── 11_set_borders.xml              # Main-window borders
    ├── 12_boxes.xml                    # Base GUI containers
    ├── 20_gauges.xml                   # Gauges and action-icon widgets
    ├── 21_cast_console.xml              # Cast console
    ├── 22_header_icons.xml              # Header icons
    ├── 30_tab_shell.xml                # Tabbed-info container
    ├── 31_affects.xml                  # Affects, modes, SLAffects
    ├── 32_group.xml                    # Group display
    ├── 33_player.xml                   # Player display
    ├── 34_map_controls.xml             # Map and legend controls
    ├── 35_room_info.xml                # Room info and legend
    ├── 36_draw_frames.xml              # Frame stub
    ├── 40_msdp_protocol.xml            # REPORT list and protocol callback
    ├── 41_msdp_gauges.xml              # Resource/opponent updates
    ├── 42_msdp_actions.xml             # Action-state updates
    ├── 50_boot.xml                     # Immediate layout boot and GUI.init
    ├── 51_event_registry.xml           # Owned event-handler registration
    ├── 52_refresh.xml                  # initializeOrRefresh
    ├── 53_lifecycle.xml                # Load/install/connect handlers
    ├── 60_layout_profiles.xml          # Adjustable-container profiles
    ├── 70_custom_scrollbar.xml         # Scrollbar styling
    └── 71_delete_line_prompt.xml       # Prompt-line utility
```

The implemented responsibilities and load order are explicit. The wrapper is
82 physical lines, and the largest child script is 269 Lua lines.

## Builder Support

`theGUI/build.py` now provides a general, explicit include mechanism. Wrappers
use build-only XML comments such as:

```xml
<!-- BUILD_INCLUDE: gui/10_layout_shell.xml -->
```

The precise spelling is an implementation detail, but the resolver must:

- Resolve paths relative to the including fragment.
- Use explicit paths rather than globs so order is reviewable.
- Reject missing include files.
- Reject include cycles.
- Prevent includes from escaping the `theGUI` source tree.
- Validate each included XML fragment independently.
- Validate the fully expanded fragment and final package.
- Remove build directives from the generated package.
- Continue supporting environments without PyYAML.
- Make `--stats` report included files separately rather than hiding them under
  the wrapper's total.
- Work with `--validate`, `--diff`, `--diff --fail-on-diff`, normal builds, and
  watch mode.

`--watch` already scans XML files recursively, but it must be verified with the
new directory. The destructive `--extract` workflow must either preserve the
composite layout or refuse clearly when it cannot; it must not silently collapse
the project back into one monolithic GUI fragment.

## Migration Phases

### Phase 1: Add composite-fragment support

- [x] Add build include parsing and expansion.
- [x] Add missing-file, invalid-fragment, traversal, and cycle diagnostics.
- [x] Update build statistics for included fragments.
- [x] Verify watch-mode discovery.
- [x] Guard or update `--extract` for composite sources.
- [x] Add focused Python tests for the include mechanism.

No production XML or Lua should move in this phase.

### Phase 2: Mechanical one-node-per-fragment extraction

- [x] Create `theGUI/src/scripts/gui/`.
- [x] Reduce `01_gui.xml` to the outer/nested group scaffolding and ordered
  include directives.
- [x] Move the existing `CSSman` subgroup unchanged.
- [x] Move each existing `Script` node unchanged into a child fragment.
- [x] Retain the nested GUI group-level bootstrap script in the wrapper unless
  the builder supports preserving it elsewhere without changing output.
- [x] Preserve the exact current child order.
- [x] Confirm `python3 theGUI/build.py --diff --fail-on-diff` reports no drift.

This phase should be its own commit. It must not contain Lua cleanup, formatting,
renaming, or behavior changes.

### Phase 3: Split the large `MSDP` node

Split the existing `MSDP` script at its natural function boundaries:

1. `40_msdp_protocol.xml`
   - `GUI.MSDP_REPORT_VARS`
   - `GUI.requestMSDPReports()`
   - `GUI.onProtocolEnabled()`
2. `41_msdp_gauges.xml`
   - Health
   - Movement
   - PSP
   - Opponent gauge updates
3. `42_msdp_actions.xml`
   - Action-icon updates

Preserve these rules:

- New subscriptions go through `GUI.MSDP_REPORT_VARS`.
- `GUI.onProtocolEnabled` must exist before its file-scope event registration.
- No mapper/protocol event may be registered a second time.
- Display functions must keep safe MSDP fallbacks.

This phase changes the internal Mudlet script-node layout, so generated XML
drift is expected and must be reviewed.

### Phase 4: Split the large `Config` node

Split the current `Config` script into four orchestration fragments:

1. `50_boot.xml`
   - Immediate background/border/box creation.
   - `GUI.validateCoreLayout()`.
   - `GUI.init()`.
2. `51_event_registry.xml`
   - The centralized owned `eventHandlers` table.
   - Handler-ID cleanup and idempotent registration.
   - Delayed verification refreshes.
3. `52_refresh.xml`
   - `GUI.initializeOrRefresh()`.
4. `53_lifecycle.xml`
   - `sysLoadEvent` reset-profile recovery.
   - `sysInstall` registration.
   - GUI `sysProtocolEnabled` registration.
   - Connection refresh registration.

The immediate boot block must remain file-scope code. Do not move it inside
`GUI.init()` merely as part of the split.

### Phase 5: Update source-aware tests and documentation

`tests/test_lifecycle_regressions.py` currently assumes all GUI source is in
`theGUI/src/scripts/01_gui.xml`. Replace that assumption with a helper that
assembles the GUI source in build order or parses an in-memory build and locates
scripts by their XML `<name>`.

- [x] Remove the hardcoded single-file GUI source path.
- [x] Locate production Lua by script name, not by physical file layout.
- [x] Update the manifest load-order assertion for the composite GUI entry.
- [x] Preserve the orphan-widget and handler-ownership regression tests.
- [x] Add an assertion covering expected GUI script names/order.
- [x] Update `theGUI/README_theGUI.md`.
- [x] Update `docs/ongoing_projects/source-to-build.md` or mark its older layout
  proposal superseded.
- [x] Replace stale `01_gui.xml:<line>` references in
  `docs/MUDLET_COMPATIBILITY.md` with fragment paths or function names.

### Phase 6: Full validation and Mudlet testing

Automated checks:

```bash
python3 theGUI/build.py --validate
python3 theGUI/build.py --diff --fail-on-diff
python3 tests/run_tests.py --skip-optional
python3 scripts/validate_package.py
```

Automated result for build `2.0.4.035` (2026-07-31): all four commands pass.
The full runner reports 6/6 supported suites and the lifecycle suite reports
26/26 cases. `luacheck` is not installed, so the documented `--skip-optional`
path was used. The package contains 78 syntax-valid Lua scripts. The build
directive leak check is empty, and the generated XML is synchronized with the
sources.

Mudlet is not installed in the implementation environment. The hands-on 4.22
and 4.21 checks below therefore remain release-owner validation items and are
not represented as complete by the automated mocks.

After phases that intentionally change the generated XML, run a normal build
once, review the version/archive/output changes, and rerun the full suite.

Manual Mudlet checks should cover:

- [ ] Fresh package import.
- [ ] In-place upgrade from the preceding package layout.
- [ ] Fresh connection and reconnection.
- [ ] `resetProfile()` recovery.
- [ ] MSDP protocol activation and report subscriptions.
- [ ] Repeated `fix gui`/refresh operations without handler growth.
- [ ] Player, group, affects, gauges, opponent, and action updates.
- [ ] ASCII/Mudlet map switching.
- [ ] Chat initialization inside the GUI chat container.
- [ ] Container save/load/profile behavior.
- [ ] Widget parenting and z-order.

Test current Mudlet 4.22 and, when practical, 4.21 because lifecycle, callback,
and handler-ID behavior changed across those releases.

## Load-Order Invariants

The final source order must continue to guarantee:

1. `00_debug.xml` loads first.
2. `00_adjustablecontainers.xml` defines the container foundation before the
   mapper and GUI create containers.
3. `00_msdpmapper.xml` retains its file-scope mapper/protocol registrations.
4. GUI component constructors are defined before GUI orchestration invokes
   them.
5. Immediate GUI shell creation happens before YATCO initializes.
6. `02_yatcoconfig.xml` and `03_yatco.xml` remain after the GUI shell.
7. `99_debug_instrumentation.xml` remains last.

Within the GUI subsystem:

- `GUI.registerEventHandlers()` must remain idempotent.
- It may kill and replace only entries owned by its local handler table.
- It must not sweep legacy mapper/file-scope IDs.
- Mapper handlers must not be duplicated in the GUI event table.
- `msdp.ROOM` continues to have two different handlers intentionally:
  `GUI.updateRoom` and the file-scope `map.eventHandler`.

## Non-Goals

The initial split does not authorize:

- Redesigning the GUI.
- Renaming public `GUI.*` functions.
- Replacing Adjustable.Container or Geyser APIs.
- Changing MSDP subscriptions or handler ownership.
- Cleaning up unrelated Lua style issues.
- Editing `LuminariGUI.xml` directly.
- Running `build.py --extract` as the migration mechanism.

Behavior cleanup should follow in separate changes after the new boundaries are
stable.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Script execution order changes | Explicit include order and an XML order regression test |
| Mudlet leaves old nodes during upgrade | Preserve topology in phase 2; manually test phases 3-4 as in-place upgrades |
| Duplicate event handlers | Retain the centralized ownership table and repeated-refresh regression tests |
| Invalid partial XML | Every included file remains independently valid XML |
| Build-only directives leak into release | Assert directives are absent from assembled output |
| Tests silently exercise stale built XML | Assemble from current sources in the test helper |
| `--extract` destroys modular layout | Preserve it or fail loudly before writing |
| Refactor mixes behavior changes with movement | Separate commits/phases and require a no-diff mechanical phase |

## Completion Criteria

The project is complete when:

- [x] `01_gui.xml` is a small wrapper/index rather than a 3,000-line source.
- [x] GUI behavior is maintained in focused files under `src/scripts/gui/`.
- [x] No GUI child fragment exceeds approximately 300 Lua lines without an
  explicit justification.
- [x] The builder validates included fragments and reports useful failures.
- [x] Phase 2 produces an unchanged generated package.
- [ ] Later intentional XML changes are reviewed and tested as upgrades.
  Automated topology, handler-ownership, and reset-profile regressions pass;
  the manual in-place upgrade remains pending.
- [x] The complete automated test suite passes.
- [x] Package validation passes.
- [ ] Manual Mudlet lifecycle and UI checks pass.
- [x] Documentation and source-aware tests no longer assume one monolithic GUI
  file.
