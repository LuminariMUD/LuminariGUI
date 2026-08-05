# Lua static analysis

LuminariGUI's production Lua is embedded in XML. All standalone Lua tools must
consume the decoded workspace created by `scripts/extract_embedded_lua.py`, not
parse `LuminariGUI.xml` independently and not rewrite `theGUI/src/`.

## Shared workspace

From the repository root:

```bash
LUMINARI_LUA_WORKSPACE="$(mktemp -d)"
python3 scripts/extract_embedded_lua.py \
  --output "${LUMINARI_LUA_WORKSPACE}/workspace"
cp -R stubs "${LUMINARI_LUA_WORKSPACE}/workspace/stubs"
cp .luarc.json "${LUMINARI_LUA_WORKSPACE}/workspace/.luarc.json"
```

The workspace contains stable files under `lua/` and `manifest.json`. The
manifest maps each file and Lua line to its physical XML fragment, Mudlet item
path, and XML line. The output directory must be absent or empty and cannot be
inside `theGUI/src/`.

`luac` and `luacheck` use this adapter through the normal test runner. LuaLS,
StyLua, Semgrep, and future LuaCov jobs use the same representation.

## Pinned tools and policy

| Tool | Pin | Enforcement |
|---|---|---|
| Lua | 5.1 from Ubuntu 24.04 | Syntax and test failures block |
| luacheck | 0.23.0 from LuaRocks | Existing critical/error policy blocks |
| Lua Language Server | 3.18.2 Linux x64, SHA-256 `ca71415dd19f19e30aaa35a4915aefca9fdb5fec31b98331cc3d77f778d539c5` | Error diagnostics block; warnings are report-only |
| StyLua | 2.5.2 Linux x64, SHA-256 `bcb0d855e91f102f28a370e850f8566b3b44b79e6274d806ea5246837c0fd5ab` | Parse/tool failures block; format differences are report-only |
| Semgrep | 1.172.0 image digest `sha256:65dcd4408adda7c183a6b4550cb1e9b19f7f627a6fbb7e0559bd466bedc44d7b` | Rule/scanner errors block; security findings are report-only pending triage |

The LuaLS release currently prints `3.18.2-dev` from its official 3.18.2 Linux
asset; CI asserts that exact embedded version string as well as the archive
checksum. Definitions in `stubs/mudlet/4.22/` cover only the Mudlet/Geyser
surface used by this package and are never loaded by Mudlet.

Current initial baselines are:

- LuaLS: 112 warnings, zero errors across 23 files;
- StyLua: 79 files with 572 differing ranges; and
- Semgrep: 23 findings (10 warning and 13 informational), zero scanner errors.

These counts are observations, not thresholds. Normalized JSON artifacts are
the review source and refer to XML paths and item names. Raw tool reports are
retained for troubleshooting.

## Local commands

With LuaLS and StyLua installed at the pinned versions:

```bash
mkdir -p \
  "${LUMINARI_LUA_WORKSPACE}/luals-log" \
  "${LUMINARI_LUA_WORKSPACE}/luals-meta"

lua-language-server \
  --check="${LUMINARI_LUA_WORKSPACE}/workspace" \
  --checklevel=Warning \
  --check_format=json \
  --check_out_path="${LUMINARI_LUA_WORKSPACE}/luals-raw.json" \
  --configpath="${LUMINARI_LUA_WORKSPACE}/workspace/.luarc.json" \
  --logpath="${LUMINARI_LUA_WORKSPACE}/luals-log" \
  --metapath="${LUMINARI_LUA_WORKSPACE}/luals-meta"

stylua \
  --check \
  --config-path .stylua.toml \
  --output-format Json \
  "${LUMINARI_LUA_WORKSPACE}/workspace/lua" \
  > "${LUMINARI_LUA_WORKSPACE}/stylua-raw.jsonl"
```

Both commands normally exit 1 at the current report-only baseline. Map their
reports before review:

```bash
python3 scripts/remap_lua_diagnostics.py \
  --tool luals \
  --manifest "${LUMINARI_LUA_WORKSPACE}/workspace/manifest.json" \
  --input "${LUMINARI_LUA_WORKSPACE}/luals-raw.json" \
  --output "${LUMINARI_LUA_WORKSPACE}/luals-normalized.json"

python3 scripts/remap_lua_diagnostics.py \
  --tool stylua \
  --manifest "${LUMINARI_LUA_WORKSPACE}/workspace/manifest.json" \
  --input "${LUMINARI_LUA_WORKSPACE}/stylua-raw.jsonl" \
  --output "${LUMINARI_LUA_WORKSPACE}/stylua-normalized.json"
```

Verify and run the custom Semgrep rules through the pinned container:

```bash
SEMGREP_IMAGE="semgrep/semgrep@sha256:65dcd4408adda7c183a6b4550cb1e9b19f7f627a6fbb7e0559bd466bedc44d7b"

docker run --rm \
  --volume "${PWD}:/src:ro" \
  --workdir /src \
  "${SEMGREP_IMAGE}" \
  python3 scripts/test_semgrep_rules.py

docker run --rm \
  --volume "${PWD}:/src:ro" \
  --volume "${LUMINARI_LUA_WORKSPACE}/workspace:/analysis:ro" \
  --workdir /src \
  "${SEMGREP_IMAGE}" \
  semgrep scan \
    --config semgrep/rules/luminari-lua-security.yml \
    --json --metrics=off --quiet /analysis/lua \
  > "${LUMINARI_LUA_WORKSPACE}/semgrep-raw.json"

python3 scripts/remap_lua_diagnostics.py \
  --tool semgrep \
  --manifest "${LUMINARI_LUA_WORKSPACE}/workspace/manifest.json" \
  --input "${LUMINARI_LUA_WORKSPACE}/semgrep-raw.json" \
  --output "${LUMINARI_LUA_WORKSPACE}/semgrep-normalized.json"
```

Semgrep's native fixture annotation parser in 1.172.0 does not recognize Lua's
`--` comment syntax. `scripts/test_semgrep_rules.py` therefore scans explicit
positive and negative Lua fixtures and requires exactly one positive and zero
negative findings for every local rule.

## Maintenance

- Review tool releases monthly and after Dependabot workflow updates.
- Recompute and review binary checksums or image digests before changing a pin.
- Run the complete fixture and package baselines before accepting an update.
- Update the versioned stub directory only against the corresponding supported
  Mudlet documentation/runtime.
- Do not make StyLua blocking until a dedicated source-formatting change has
  been manually reviewed and shown to preserve built XML and runtime behavior.

References: [LuaLS diagnosis reports](https://luals.github.io/wiki/diagnosis-report/),
[LuaLS configuration](https://luals.github.io/wiki/configuration/),
[StyLua](https://github.com/JohnnyMorganz/StyLua), and
[Semgrep CI](https://semgrep.dev/docs/semgrep-ci/sample-ci-configs).
