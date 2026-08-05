# Coverage reporting

LuminariGUI publishes two independent, informational coverage reports. They
must never be combined into a repository-wide percentage:

- **Application Lua** covers production Lua from `theGUI/src/` that the
  lifecycle regression suite actually executes under Mudlet mocks.
- **Python tooling** covers `theGUI/*.py`, `scripts/*.py`, and the test runner
  while the coverage, extractor, lifecycle, build, package, validation, and
  release-tooling regressions run. Test implementation modules are outside
  this total.

Neither report replaces a real Mudlet import and runtime smoke test. No
coverage threshold is blocking while baseline history is collected.

## Source attribution

`scripts/extract_embedded_lua.py` creates the same stable 79-file workspace
used by LuaLS, StyLua, luacheck, and Semgrep. During coverage collection,
`tests/test_lifecycle_regressions.py` surrounds interpolated production blocks
with inert marker comments but keeps each block in its original generated test
chunk. This preserves access to the test's local Mudlet mocks.

LuaCov first records the generated driver paths. `scripts/lua_coverage_cli.py map`
then validates every marker, snippet hash, offset, and driver path before
moving hits onto the corresponding extracted Lua file. The checked-in
`luminari` LuaCov reporter applies LuaCov's own executable-line scanner to the
mapped stats. The final JSON, LCOV, and HTML reports identify physical XML
fragments, Mudlet item paths, and XML line numbers; normalized reports contain
no temporary paths.

## Deliberate exclusions and boundaries

- Generated lifecycle drivers and Mudlet mock/setup lines are excluded from
  production totals. Their total and hit-line count are retained as a separate
  category in `lua-source-map.json` and the job summary.
- Empty XML `<script>` elements are excluded because the shared extractor does
  not materialize them. The manifest records their count.
- LuaCov classifies blank lines, comments, and other non-executable Lua lines
  as excluded. No inline source exclusions are currently used.
- All 79 nonempty production scripts are included in the Lua denominator.
  Scripts and branches that require real Geyser, Qt, mapper, network, sound,
  callback, or live MSDP behavior remain visibly missed unless a mock-based
  test executes them.
- Python test modules are excluded from the tooling denominator through
  `pyproject.toml`; `tests/run_tests.py` remains included as production test
  orchestration. Coverage.py's `subprocess` patch and relative paths include
  isolated build/package/release subprocesses without retaining their deleted
  temporary-copy names. The Python artifact still includes branch data, while
  the concise summary compares line coverage only.
- Coverage artifacts are evidence about automated tests, not approval for a
  release. The Mudlet checklist remains a separate gate.

## Pinned tools

- Coverage.py `7.15.3`, installed from hash-locked `requirements-ci.txt`
- LuaCov `0.17.0-1`
- LuaCov's `datafile` dependency `0.11-1`
- Lua `5.1` and luacheck `0.23.0`

GitHub Actions retains raw driver stats, mapped production stats, source-map
metadata, the shared extraction manifest, separate Lua/Python HTML and
machine-readable reports, and the concise summary for 30 days.

## Local reproduction

Install the Python lock and Lua tools in an isolated environment, then run the
same collection steps as `Coverage / report`:

```bash
python3 -m venv /tmp/luminari-coverage-venv
/tmp/luminari-coverage-venv/bin/python -m pip install \
  --require-hashes -r requirements-ci.txt

sudo luarocks --lua-version=5.1 install luacheck 0.23.0
sudo luarocks --lua-version=5.1 install datafile 0.11-1
sudo luarocks --lua-version=5.1 install luacov 0.17.0-1 --deps-mode=none

coverage_root="$(mktemp -d -t luminari-coverage-XXXXXX)"
export COVERAGE_FILE="${coverage_root}/python/.coverage"
export LUMINARI_LUA_WORKSPACE="${coverage_root}/lua-workspace"
export LUMINARI_LUA_COVERAGE_DIR="${coverage_root}/lua"
export LUMINARI_LUACOV_STATS_FILE="${coverage_root}/lua/luacov.raw.stats.out"
export LUMINARI_LUACOV_REPORT_FILE="${coverage_root}/lua/luacov-lines.tsv"
export LUACOV_CONFIG="${PWD}/tests/test_configs/luacov_config.lua"
mkdir -p "${coverage_root}/python" "${coverage_root}/lua"

python3 scripts/extract_embedded_lua.py --output "${LUMINARI_LUA_WORKSPACE}"
/tmp/luminari-coverage-venv/bin/coverage run tests/test_coverage_reporting.py
/tmp/luminari-coverage-venv/bin/coverage run \
  tests/test_embedded_lua_extractor.py
/tmp/luminari-coverage-venv/bin/coverage run \
  tests/test_lifecycle_regressions.py
/tmp/luminari-coverage-venv/bin/coverage run theGUI/build.py --validate
/tmp/luminari-coverage-venv/bin/coverage run \
  theGUI/build.py --diff --fail-on-diff
/tmp/luminari-coverage-venv/bin/coverage run scripts/validate_package.py
/tmp/luminari-coverage-venv/bin/coverage run \
  scripts/analyze_handlers.py --fail-on-unowned
/tmp/luminari-coverage-venv/bin/coverage combine

/tmp/luminari-coverage-venv/bin/coverage run \
  scripts/lua_coverage_cli.py map \
  --workspace "${LUMINARI_LUA_WORKSPACE}" \
  --raw-stats "${LUMINARI_LUACOV_STATS_FILE}" \
  --drivers "${LUMINARI_LUA_COVERAGE_DIR}/drivers" \
  --collection-cwd "${PWD}" \
  --output-stats "${LUMINARI_LUA_COVERAGE_DIR}/lua-production.stats.out" \
  --output-map "${LUMINARI_LUA_COVERAGE_DIR}/lua-source-map.json"

(
  cd "${LUMINARI_LUA_WORKSPACE}"
  LUMINARI_LUACOV_STATS_FILE="${LUMINARI_LUA_COVERAGE_DIR}/lua-production.stats.out" \
  LUA_PATH="${OLDPWD}/scripts/?.lua;;" \
    luacov -c "${LUACOV_CONFIG}" -r luminari
)

/tmp/luminari-coverage-venv/bin/coverage run \
  scripts/lua_coverage_cli.py render \
  --workspace "${LUMINARI_LUA_WORKSPACE}" \
  --line-report "${LUMINARI_LUACOV_REPORT_FILE}" \
  --mapping "${LUMINARI_LUA_COVERAGE_DIR}/lua-source-map.json" \
  --output-json "${LUMINARI_LUA_COVERAGE_DIR}/lua-coverage.json" \
  --output-lcov "${LUMINARI_LUA_COVERAGE_DIR}/lua-coverage.lcov" \
  --output-html "${LUMINARI_LUA_COVERAGE_DIR}/html/index.html"
/tmp/luminari-coverage-venv/bin/coverage combine --append

/tmp/luminari-coverage-venv/bin/coverage json \
  -o "${coverage_root}/python/coverage.json"
/tmp/luminari-coverage-venv/bin/coverage xml \
  -o "${coverage_root}/python/coverage.xml"
/tmp/luminari-coverage-venv/bin/coverage html \
  -d "${coverage_root}/python/html"

python3 scripts/lua_coverage_cli.py summary \
  --lua "${LUMINARI_LUA_COVERAGE_DIR}/lua-coverage.json" \
  --python "${coverage_root}/python/coverage.json" \
  --baseline coverage/baselines.json \
  --output-json "${coverage_root}/coverage-summary.json" \
  --output-markdown "${coverage_root}/coverage-summary.md"
```

The initial 2026-08-05 baseline is 860/2,833 application-Lua lines (30.36%)
and 1,489/2,892 Python-tooling lines (51.49%). Append reviewed `master`
checkpoints to `coverage/baselines.json`; do not reinterpret the baseline as a
minimum. Threshold discussion starts only after at least two weeks of stable
history and explicit review of Mudlet-only paths.
