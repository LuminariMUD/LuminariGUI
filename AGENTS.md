# Repository guidance

LuminariGUI is a Mudlet GUI package for LuminariMUD, written in Lua embedded
in XML. Edit this canonical file; preserve the relative `CLAUDE.md` and
`GEMINI.md` symlinks.

## Source and build

- Edit `theGUI/src/`, not generated `LuminariGUI.xml`.
- `theGUI/build.yaml` defines version and assembly order. Script wrappers
  `01_gui.xml` and `03_yatco.xml` include `gui/` and `yatco/` children.
- Keep GUI children around 300 Lua lines or fewer; match existing fragment
  names and structure.
- Run commands from the repository root. `python3 theGUI/build.py` increments
  the version, archives the old XML, and rebuilds. Use `--version <ver>` for
  an exact version; avoid unnecessary rebuilds.
- Commit source changes with `theGUI/build.yaml`, `LuminariGUI.xml`, and the
  generated archive. Use `--extract`, `--clean`, or `--watch` only when their
  overwrite, deletion, or repeated-build behavior is intended.

## Validation

Before pushing source changes, run:

```bash
python3 theGUI/build.py --validate
python3 theGUI/build.py --diff --fail-on-diff
python3 tests/run_tests.py --skip-optional
python3 scripts/validate_package.py
python3 scripts/analyze_handlers.py --fail-on-unowned
```

These checks are read-only. Without `--skip-optional`, missing external tools
abort the runner before any suites run. For full CI validation, install the
pinned tools, omit that flag, and follow [docs/CI.md](docs/CI.md).

Map generated XML lines to source with
`python3 scripts/map_generated_line.py <line>`; it rejects stale builds.
Other command options are documented in [docs/PYTHON_TOOLS.md](docs/PYTHON_TOOLS.md).

## Runtime conventions

- Namespace GUI code under `GUI`; initialize tables safely and provide MSDP
  fallbacks, e.g. `tonumber(msdp.HEALTH) or 0`.
- Add GUI event handlers to `GUI.EVENT_HANDLERS` in
  `theGUI/src/scripts/gui/51_event_registry.xml`. Registration must be
  idempotent and replace only owned entries; never sweep all of
  `GUI.eventHandlerIds` or duplicate file-scope mapper handlers.
- Register lifecycle handlers through the helper in `gui/53_lifecycle.xml`.
  Use `GUI.setOwnedTimer()` with stable names, never raw `tempTimer()`.
  See [docs/RESOURCE_LIFECYCLE.md](docs/RESOURCE_LIFECYCLE.md) for ownership
  and cleanup rules.
- Add MSDP subscriptions to `GUI.MSDP_REPORT_VARS` in `gui/40_msdp_protocol.xml`.
  Profile reset clears `msdp` without connection/protocol events: recreate
  the table, initialize maps, request reports, and refresh.
- Use forward-slash paths. Styles are Qt QSS: `box-shadow` is unsupported;
  use `border-image` for stretched images.
- Preserve `<packageName>`, `<script>`, and `<eventHandlerList>` on script
  groups and leaves. Escape XML special characters. Sibling names must be
  unique within each Mudlet item family, including group/leaf pairs;
  identical names in different parents or package sections are allowed.

## Compatibility and releases

Read [docs/MUDLET_COMPATIBILITY.md](docs/MUDLET_COMPATIBILITY.md) when diagnosing
client behavior; the documented target is Mudlet 4.22.0. Runtime validation is
described in [docs/MUDLET_SMOKE_TEST.md](docs/MUDLET_SMOKE_TEST.md); automated
tests do not establish manual checks as passed.

- Local package: `python3 theGUI/package.py create`.
- Publish release: `python3 theGUI/package.py release`.
- Preview publication: `python3 theGUI/package.py release --dry-run`.

Both package commands build and test; `--version <ver>` selects an exact
version, and `--skip-build` requires matching manifest/XML versions.
`release` atomically pushes `master`, the release branch, and tag, then
publishes the GitHub Release with `.mpackage` and JSON metadata. Confirm
`fully published and verified`, remote refs with `git ls-remote`, and assets
with `gh release view` before reporting completion.

For every new release, use `.env` variables `UPLOAD_SSH_COMMAND` and
`UPLOAD_SSH_PATH` to upload the release package to the server under its
existing versioned filename, then duplicate it in the same remote directory
as `LuminariGUI.mpackage`. Verify both remote files match the release package
before reporting completion; do not print or commit `.env` values.

Public downloads use a separate Cloudflare Pages deployment. Local `.env`
contains its credentials, project/branch, website Git URL, build/download
paths, and public URL; `.env.example` documents the steps. Clone the website
into a temporary directory if needed, update both download copies, build,
commit/push, and deploy the complete site. Never deploy only the packages.
Verify both files at `RELEASE_PUBLIC_BASE_URL` match the release SHA-256 after
redirects; SSH file checks alone do not verify public downloads.
