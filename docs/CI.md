# Continuous Integration

LuminariGUI uses four GitHub Actions workflows. CI validates the source
fragments and the committed generated package without rebuilding or bumping
the version. Security scans the repository and extracted Lua. Coverage reports
Lua application and Python tooling totals separately. Mudlet is a manual,
advisory official-AppImage launch experiment.

The workflows do not replace the real-client release checklist in
[`MUDLET_SMOKE_TEST.md`](MUDLET_SMOKE_TEST.md).

## Pull-request policy

The protected `master` branch requires these GitHub Actions check runs:

| UI check | Check-run context | What blocks |
|---|---|---|
| `CI / quality` | `quality` | Python lint/format/types, LuaLS errors, analysis tool failures, unowned runtime resources, dirty checkout |
| `CI / build-and-test` | `build-and-test` | invalid/stale XML, missing Lua 5.1 tooling, any test failure, package validation failure, dirty checkout |
| `Security / gitleaks` | `gitleaks` | scanner-canary failure or a verified current/history secret finding |
| `Security / CodeQL` | `CodeQL` | Python or GitHub Actions CodeQL analysis failure/finding under the configured suite |
| `Security / Semgrep Lua` | `Semgrep Lua` | scanner/rule-fixture/mapping failure; existing mapped findings remain report-only |
| `Security / dependency-review` | `dependency-review` | a newly introduced supported dependency vulnerability at moderate severity or higher |

Required checks must be current with `master` before merge. Administrator
enforcement is intentionally disabled so maintainers can perform the existing
atomic release flow; ordinary pull requests cannot bypass the checks. The
`Coverage / report`, `Mudlet / smoke`, and dependency-graph checks are not
required. Coverage has no threshold, and the Xvfb job cannot prove real
runtime behavior.

## Reproduce repository checks locally

Run commands from the repository root. Python 3.12.3 is the hosted baseline.
The lock is hash-verified:

```bash
luminari_ci_root="$(mktemp -d)"
python3 -m venv "${luminari_ci_root}/venv"
"${luminari_ci_root}/venv/bin/python" -m pip install \
  --require-hashes -r requirements-ci.txt
export PATH="${luminari_ci_root}/venv/bin:${PATH}"
```

Do not use a repository directory for generated reports, caches, extracted
Lua, or virtual environments. This keeps the final clean-tree assertion
meaningful.

### `CI / quality`

Install Lua 5.1, its compiler/development files, LuaRocks, `jq`, and `unzip`.
Install luacheck 0.23.0 for Lua 5.1. The commands below are the repository
logic in the required quality job:

```bash
lua -e 'assert(_VERSION == "Lua 5.1", _VERSION)'
luacheck --version
ruff check --no-cache theGUI scripts tests
ruff format --check --no-cache theGUI scripts tests
mypy --cache-dir "${luminari_ci_root}/mypy-cache"
PYTHONPYCACHEPREFIX="${luminari_ci_root}/pycache" \
  python -m compileall -q theGUI scripts tests

lua_workspace="${luminari_ci_root}/lua-analysis/workspace"
python scripts/extract_embedded_lua.py --output "${lua_workspace}"
cp -R stubs "${lua_workspace}/stubs"
cp .luarc.json "${lua_workspace}/.luarc.json"
python scripts/analyze_handlers.py --fail-on-unowned
test -z "$(git status --porcelain --untracked-files=all)"
```

The job additionally downloads checksum-pinned LuaLS 3.18.2 and StyLua 2.5.2
under the runner temporary directory. Run the exact download, checksum,
diagnostic-remapping, and error-count commands from the corresponding steps in
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml). LuaLS errors block;
its warnings and StyLua formatting differences are report-only, while either
tool failing to execute or map its output blocks.

### `CI / build-and-test`

With Lua 5.1 and luacheck 0.23.0 installed:

```bash
python theGUI/build.py --validate
python theGUI/build.py --diff --fail-on-diff
(
  cd tests
  python run_tests.py \
    --parallel \
    --report "${luminari_ci_root}/test-results.json" \
    --format json
)
python scripts/validate_package.py
test -z "$(git status --porcelain --untracked-files=all)"
```

Do not pass `--skip-optional` when reproducing CI. A missing external tool is a
setup failure in the required job.

### `Security / gitleaks`

The workflow uses Gitleaks 8.18.4 with the Linux x64 archive SHA-256
`ba6dbb656933921c775ee5a2d1c13a91046e7952e9d919f9bac4cec61d628e7d`.
After installing that exact binary outside the checkout, reproduce the scan:

```bash
gitleaks detect \
  --source . \
  --config .gitleaks.toml \
  --redact \
  --no-banner \
  --no-color \
  --report-format json \
  --report-path "${luminari_ci_root}/gitleaks-report.json"
```

Pull requests scan `BASE_SHA..HEAD_SHA`; `master` and the weekly schedule scan
complete history. CI also generates a temporary split-string token canary and
requires Gitleaks to detect it without exposing it. The exact canary block is
in [`.github/workflows/security.yml`](../.github/workflows/security.yml).

### `Security / Semgrep Lua`

Docker is the supported local route because it reproduces the pinned Semgrep
image digest. Extract once, then run the rule fixtures and production scan:

```bash
semgrep_root="${luminari_ci_root}/semgrep-lua"
python scripts/extract_embedded_lua.py --output "${semgrep_root}/workspace"
docker run --rm \
  --volume "${PWD}:/src:ro" \
  --workdir /src \
  semgrep/semgrep@sha256:65dcd4408adda7c183a6b4550cb1e9b19f7f627a6fbb7e0559bd466bedc44d7b \
  python3 scripts/test_semgrep_rules.py
docker run --rm \
  --volume "${PWD}:/src:ro" \
  --volume "${semgrep_root}/workspace:/analysis:ro" \
  --workdir /src \
  semgrep/semgrep@sha256:65dcd4408adda7c183a6b4550cb1e9b19f7f627a6fbb7e0559bd466bedc44d7b \
  semgrep scan \
    --config semgrep/rules/luminari-lua-security.yml \
    --json --metrics=off --quiet /analysis/lua \
    > "${semgrep_root}/semgrep-raw.json"
python scripts/remap_lua_diagnostics.py \
  --tool semgrep \
  --manifest "${semgrep_root}/workspace/manifest.json" \
  --input "${semgrep_root}/semgrep-raw.json" \
  --output "${semgrep_root}/semgrep-normalized.json"
jq -e '.tool_error_count == 0' "${semgrep_root}/semgrep-normalized.json"
```

### GitHub-hosted checks

`Security / CodeQL` and `Security / dependency-review` depend on GitHub's
CodeQL runner integration and repository dependency graph. Their repository
inputs are reviewable locally—the Python/Actions source, pinned workflow, pip
lock, and action SHAs—but there is no honest byte-for-byte offline equivalent
for the hosted check result. Exercise them on a pull request and inspect the
named check:

```bash
gh pr checks <pull-request-number>
```

CodeQL CLI may be used for additional local Python analysis, but it does not
replace the required GitHub check. Dependency review evaluates only the PR
delta; the documented vulnerable and documentation-only canary PRs establish
the repository baseline.

## Informational workflows

Coverage reproduction, exclusions, and baseline policy are in
[`COVERAGE.md`](COVERAGE.md). Run the manual Xvfb experiment with:

```bash
gh workflow run mudlet.yml --ref master
gh run list --workflow mudlet.yml --limit 1
```

The accepted portable-profile baseline is hosted
[run 31052249656](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31052249656):
its retained log reports Mudlet 4.22.0, Qt 6.9, and the isolated
`/home/runner/work/_temp/mudlet-smoke/portable` configuration directory. That
acceptance covers official-binary launch and package queuing only.

Complete [`MUDLET_SMOKE_TEST.md`](MUDLET_SMOKE_TEST.md) before a release even
when both informational workflows are green.

## Troubleshooting and triage

- **Lua version mismatch:** `lua -e 'print(_VERSION)'` must print `Lua 5.1`.
  Do not make the suite pass with Lua 5.4; put Lua 5.1's `lua` and `luac`
  commands first on the temporary `PATH`.
- **Missing optional dependency:** a required CI reproduction deliberately
  omits `--skip-optional`. Install the named executable and rerun rather than
  accepting a reduced suite.
- **Generated-output drift:** run `python3 theGUI/build.py --diff` to inspect
  it. Edit `theGUI/src/`, perform one intentional build, and commit the source,
  manifest, generated XML, and archive together.
- **Generated XML line:** run `python3 scripts/map_generated_line.py LINE` to
  map a package diagnostic to the physical wrapper or included fragment. The
  command refuses stale XML; use `--json` when feeding another diagnostic
  tool.
- **Source-map error:** delete only the temporary extracted workspace,
  re-extract it, and confirm its `manifest.json` matches the current commit.
  Never patch decoded temporary Lua or suppress a random temporary path.
- **Gitleaks finding:** rotate a real credential first. Add an allow-list entry
  only for a reviewed false positive, narrowed by rule/fingerprint/path; never
  exclude all XML, JSON, Lua, source fragments, or release artifacts.
- **Semgrep finding:** inspect the mapped physical XML/item/line. New or
  changed rules need positive and negative fixtures. Existing findings remain
  report-only, but scanner or mapping errors are blocking.
- **LuaLS or luacheck false positive:** prefer a versioned Mudlet/Geyser stub or
  a narrow global declaration. Do not disable an entire diagnostic family.
- **Dependency review false positive:** inspect the manifest and advisory,
  document why it is unreachable if appropriate, and use GitHub's scoped
  dismissal mechanism. Do not weaken `fail-on-severity` repository-wide.
- **Action failure after an update:** verify the action's full commit SHA and
  release notes. Never replace a pinned SHA with a floating tag to get green.

## Ownership, cadence, and retention

| Surface | Owner | Review cadence | Artifact retention |
|---|---|---|---:|
| Core build/test and Python lock | Repository maintainers | Every tool PR; weekly Dependabot batch | 14 days |
| LuaLS, StyLua, Lua 5.1, luacheck | Lua/Mudlet maintainers | Monthly and on Mudlet minor releases | 14 days |
| Gitleaks and `.gitleaks.toml` | Repository security maintainers | Weekly scheduled scan; every finding | 30 days |
| CodeQL and Actions pins | Repository security maintainers | Weekly scheduled scan; weekly Dependabot batch | GitHub code-scanning retention |
| Semgrep rules and fixtures | Lua/Mudlet plus security maintainers | Every rule change; monthly baseline review | 30 days |
| Dependency review/Dependabot | Repository maintainers | Every PR; weekly dependency batches | Check logs only |
| Lua/Python coverage | Test maintainers | Every push/PR; threshold review after stable history | 30 days |
| Experimental Mudlet Xvfb | Mudlet compatibility maintainers | Manual before releases and after Mudlet updates | 14 days |

Update a tool by changing its human-readable pin, immutable checksum/digest or
action SHA, documentation, and any fixture/baseline in one reviewable change.
Run the affected local equivalent and hosted workflow before merging.
