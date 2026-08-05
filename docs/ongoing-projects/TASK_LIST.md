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
- [ ] Audit the long-lived handlers and timers reported by
  `scripts/analyze_handlers.py`. Distinguish intentional file-scope/lifecycle
  registrations from real leaks, add ownership/cleanup where needed, and
  verify handler counts across load, reconnect, `resetProfile()`, and repeated
  `fix gui` calls.
- [ ] Implement the phased
  [comprehensive CI pipeline plan](CI_PIPELINE_PLAN.md), beginning with the
  non-mutating `python3 theGUI/build.py --diff --fail-on-diff` source/output
  drift check and full dependency-backed test run.
- [ ] Define Mudlet-aware duplicate-name rules and add scope-aware build
  validation with regression tests. Do not reject intentional same-named items
  that Mudlet permits in different groups or package sections.
- [ ] Review the remaining top-level source fragments over the old approximate
  500-line target (`00_msdpmapper.xml` and `03_yatco.xml`). Either split them
  with hierarchy-preserving composite wrappers or document why each should
  remain intact.
- [ ] Add a source-line mapping facility (`--map` or an equivalent) for
  correlating errors in generated `LuminariGUI.xml` with physical fragments,
  unless embedded markers and screen diagnostics are first shown to cover the
  same debugging need completely.

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
