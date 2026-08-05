# Project Task List

This is the single tracker for unfinished project work. Completed project plans
and durable implementation guidance belong in the canonical documentation, not
in this folder.

## Maintenance and automation

- [x] Consolidate `docs/previous_changelogs/` into one historical document or
  archive while preserving release provenance.
  - Completed 2026-08-05: combined both snapshots in
    `docs/HISTORICAL_CHANGELOG.md`, retaining source filenames, release
    entries, and their introducing commit.
  - Verified: all archived release headings are present, the old directory is
    gone, `git -c core.whitespace=cr-at-eol diff --check` passes, and
    `python3 theGUI/build.py --validate` passes.
- [x] Audit the long-lived handlers and timers reported by
  `scripts/analyze_handlers.py`. Distinguish intentional file-scope/lifecycle
  registrations from real leaks, add ownership/cleanup where needed, and
  verify handler counts across load, reconnect, `resetProfile()`, and repeated
  `fix gui` calls.
  - Completed 2026-08-05: centralized runtime handlers and named timers in
    `theGUI/src/scripts/00_resources.xml`, added exit/uninstall cleanup, and
    made the analyzer ownership-aware with a blocking unowned-resource mode.
  - Verified: lifecycle regressions pass 33/33; Mudlet 4.22 holds exactly
    5 mapper + 26 GUI + 6 lifecycle handlers across load, reconnect,
    `resetProfile()`, ten rapid and ten settled refreshes, with at most one
    recurring timer and zero owned resources after uninstall. See
    `docs/RESOURCE_LIFECYCLE.md`.
- [x] Implement the phased
  [comprehensive CI pipeline plan](CI_PIPELINE_PLAN.md), beginning with the
  non-mutating `python3 theGUI/build.py --diff --fail-on-diff` source/output
  drift check and full dependency-backed test run.
  - Phase 1 implemented and locally verified 2026-08-05: hash-locked Python
    tooling, Ruff/mypy, Lua 5.1 plus luacheck, all seven test suites,
    non-mutating build/drift/package checks, clean-tree enforcement, pinned
    Actions, timeouts, and retained JSON reports. Hosted run
    [31044018354](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31044018354)
    passed both jobs in under one minute; Phase 2 security work follows.
  - Phase 2 implemented locally 2026-08-05: checksum-pinned Gitleaks with a
    mandatory redacted canary (zero findings across 102 historical commits),
    Python/Actions CodeQL, dependency review, weekly scans, and grouped
    Dependabot updates. Hosted security
    [run 31044714531](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31044714531)
    passed; dependency review passed documentation-only
    [PR #7](https://github.com/LuminariMUD/LuminariGUI/pull/7) and rejected
    Django 1.11.0 in [PR #6](https://github.com/LuminariMUD/LuminariGUI/pull/6).
    The repository dependency graph and alerts are enabled, both canary PRs
    are closed, and both remote branches were deleted.
  - Phase 3 bridge checkpoint implemented locally 2026-08-05:
    `scripts/extract_embedded_lua.py` extracts all 79 nonempty Lua blocks in
    assembled order to stable temporary paths, emits physical XML/item/line
    mappings, and rejects unsafe or colliding outputs. The new `extractor`
    regression suite verifies byte-for-byte package parity and input
    immutability; `luac` and `luacheck` now share the adapter. All eight suites
    pass in the pinned Lua 5.1/luacheck 0.23.0 environment.
  - Phase 3 static-tool checkpoint implemented locally 2026-08-05: LuaLS
    errors now block while 112 warnings remain report-only; StyLua's 79-file
    baseline is report-only; and seven fixture-backed Semgrep rules report 23
    triage findings with scanner failures blocking. Every normalized result
    maps back to a physical XML/item/line with no temporary path. Hosted CI
    [run 31048108086](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31048108086)
    and Security
    [run 31048108103](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31048108103)
    passed every Phase 3 job; Phase 4 coverage work follows.
  - Phase 4 implemented locally 2026-08-05: LuaCov 0.17.0 maps lifecycle
    execution back to all 79 extracted production scripts while generated
    driver code remains a separately reported category. Coverage.py measures
    Python tooling only; separate JSON/LCOV-or-XML/HTML artifacts, baseline
    deltas, 30-day retention, and a ninth `coverage` regression suite are in
    place. The initial baselines are 30.36% Lua and 51.49% Python line
    coverage with no thresholds. Hosted
    [run 31050957309](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31050957309)
    passed every collection, mapping, normalization, summary, clean-tree, and
    artifact step in 99 seconds; core CI, Security, and dependency-graph runs
    for the same commit also passed. Phase 4 is accepted and Phase 5 follows.
  - Phase 5 implemented locally 2026-08-05: the canonical real-Mudlet release
    checklist now covers import, MSDP, both maps, callbacks, YATCO, aliases,
    physical keypad input, refresh/reconnect/reset, replacement/uninstall, and
    Qt6/Geyser visual behavior with explicit package-versus-upstream outcomes.
    A manual-only `Mudlet / smoke` workflow checksum-verifies the official
    4.22.0 AppImage and captures logs plus the Xvfb display while testing Qt
    startup and command-line package queuing. Hosted
    [run 31052249656](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31052249656)
    passed with Mudlet 4.22.0/Qt 6.9, a visible display capture, and the
    expected isolated portable configuration path. The experiment is accepted
    but remains advisory; the full real-client checklist is still manual.
  - Phase 6 completed 2026-08-05: `docs/CI.md` documents stable required check
    names, local/hosted reproduction boundaries, troubleshooting, ownership,
    cadence, and retention; contributor/agent/tooling docs and the README badge
    are aligned. Strict `master` protection requires `quality`,
    `build-and-test`, `gitleaks`, `CodeQL`, `Semgrep Lua`, and
    `dependency-review`, while coverage and Mudlet smoke remain informational.
    Force pushes/deletions are disabled; administrator enforcement remains off
    only for the atomic maintainer release workflow. All six phases are
    accepted.
- [x] Define Mudlet-aware duplicate-name rules and add scope-aware build
  validation with regression tests. Do not reject intentional same-named items
  that Mudlet permits in different groups or package sections.
  - Completed 2026-08-05: final-package validation now normalizes each Mudlet
    group/leaf pair into one item family and rejects only exact,
    case-sensitive sibling collisions. Same names remain valid in different
    parent groups or package sections, including the current nested `GUI` and
    `MSDPMapper` names. Regression coverage proves allowed cross-scope/case
    variants, rejects a leaf/group sibling collision with its full parent
    scope, and validates the current package.
- [x] Review the remaining top-level source fragments over the old approximate
  500-line target (`00_msdpmapper.xml` and `03_yatco.xml`). Either split them
  with hierarchy-preserving composite wrappers or document why each should
  remain intact.
  - Completed 2026-08-05: `03_yatco.xml` is now a 14-line ordered wrapper over
    complete `Shared` (122 lines) and `Tabbed Chat` (489 lines) group subtrees;
    the generated package is byte-for-byte unchanged. `00_msdpmapper.xml`
    remains one reviewed 622-line Mudlet script because its private tables and
    helpers intentionally share one Lua lexical scope; splitting it into items
    would expose internals and change in-session reload semantics. Regression
    tests cap that exception and enforce YATCO child order, validity, and size.
- [x] Add a source-line mapping facility (`--map` or an equivalent) for
  correlating errors in generated `LuminariGUI.xml` with physical fragments,
  unless embedded markers and screen diagnostics are first shown to cover the
  same debugging need completely.
  - Completed 2026-08-05: `scripts/map_generated_line.py LINE` reconstructs
    the canonical package with provenance from the builder's recursive include
    resolver and maps skeleton, top-level, wrapper, and included-child lines to
    exact physical fragments. It reports manifest context, offers JSON, and
    refuses stale XML. Regression coverage verifies all mapping classes,
    bounds, and stale-output rejection; line 4530 currently resolves to
    `theGUI/src/scripts/gui/51_event_registry.xml:51`.

## Compatibility and release polish

- [ ] Create and bundle a 512×512 package icon, then populate the `icon` field
  in generated `config.lua`.
- [ ] Visually re-verify the remaining QSS `background` shorthand and
  `vertical-align` declarations under supported Qt6/Mudlet releases; replace
  any declarations that render inconsistently.
- [ ] Complete and record a manual Mudlet smoke test of the package aliases and
  numeric-keypad movement bindings. Automated tests cover their structure but
  not physical keyboard input in Mudlet.

## Feature backlog

- [ ] Expand sound support beyond chat notifications using a small native subsystem
