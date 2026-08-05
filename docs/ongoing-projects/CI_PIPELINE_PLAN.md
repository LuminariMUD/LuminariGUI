# Comprehensive CI Pipeline Plan

- **Status:** In progress — Phase 1 complete; Phase 2 implemented locally
- **Created:** 2026-08-05
- **Last updated:** 2026-08-05
- **Scope:** Pull-request and `master` automation for the XML/Lua package,
  Python build tools, tests, and repository security.

## Outcome

Add a comprehensive, non-mutating GitHub Actions pipeline that prevents
invalid or stale packages, Lua regressions, test failures, leaked secrets, and
supported static-analysis findings from reaching `master`.

The pipeline must remain honest about its limits. Most application code is Lua
embedded in XML and executed inside Mudlet, so CodeQL, Python coverage, and
mocked Lua tests must not be presented as complete coverage of the running GUI.
Mudlet import and runtime behavior remain a separate release-quality check.

## Repository constraints

- `theGUI/src/` is the source of truth; `LuminariGUI.xml` is generated output.
- A normal `python3 theGUI/build.py` invocation increments the version,
  archives the previous XML, and rewrites tracked files. CI must use only its
  non-mutating modes.
- Lua is stored inside XML `<script>` elements in script, trigger, alias, and
  key fragments. Most standalone Lua tools cannot analyze those files without
  an extraction adapter.
- Mudlet runs Lua 5.1 and exposes a large dynamic API through globals such as
  `Geyser`, `GUI`, `msdp`, and `registerAnonymousEventHandler`.
- The test runner already covers syntax, quality, functions, events,
  lifecycle regressions, system behavior, and performance. CI must install all
  optional tools and run the suite without `--skip-optional`.
- CodeQL supports the Python tooling and GitHub Actions workflows, but it does
  not support Lua.
- The repository currently has no `.github/workflows/`, Python dependency
  manifest, lockfile, or Lua rockspec. Dependency review will initially see
  GitHub Actions dependencies only unless a CI dependency manifest is added.
- XML is not type-checked. Its equivalent quality gates are well-formedness,
  required Mudlet structure, safe source assembly, and source/output drift
  detection.

## Target checks

| Required check | Trigger | Purpose |
|---|---|---|
| `CI / quality` | Pull request, push to `master` | Python lint/format, XML validation, generated-output drift, Lua lint and diagnostics |
| `CI / build-and-test` | Pull request, push to `master` | Non-mutating assembly, full test runner, built-package validation |
| `Security / gitleaks` | Pull request, push, scheduled | Detect secrets in current files and Git history |
| `Security / CodeQL` | Pull request, push, scheduled | Analyze Python tools and GitHub Actions workflows |
| `Security / Semgrep Lua` | Pull request, push | Apply Lua-aware and project-specific SAST rules to extracted scripts |
| `Security / dependency-review` | Pull request | Reject newly introduced vulnerable supported dependencies |
| `Coverage / report` | Pull request, push | Publish separate Lua-runtime and Python-tooling coverage; initially informational |
| `Mudlet / smoke` | Manual or release | Verify package import and real Geyser, Qt, callback, mapper, and MSDP behavior |

Required pull-request checks should complete in ten minutes or less on a warm
cache. Scheduled security scans may run longer.

## Pipeline flow

```text
theGUI/src XML fragments
  |-- non-mutating assembly --> LuminariGUI.xml validation and test runner
  `-- Lua extraction adapter --> luac, luacheck, StyLua, LuaLS, Semgrep, LuaCov

Python build/test tools --------> Ruff, mypy, CodeQL, tooling coverage
GitHub workflow files ----------> CodeQL, dependency review, Dependabot
Entire Git history -------------> Gitleaks
```

## Tooling decisions

### XML and generated package

Use the repository's build system instead of a generic XML formatter:

```bash
python3 theGUI/build.py --validate
python3 theGUI/build.py --diff --fail-on-diff
python3 scripts/validate_package.py
```

`--validate` assembles and validates in memory. `--diff --fail-on-diff`
ensures the committed `LuminariGUI.xml` matches the fragments without changing
the version or workspace.

Do not run `scripts/format_xml.py` in CI. It formats in place and can create a
backup. Generic XML reserialization can also obscure Lua whitespace and entity
changes. The initial pipeline therefore treats canonical build consistency as
the XML format gate. A future source-fragment formatter should become blocking
only after check-only operation and byte-for-byte build equivalence are
demonstrated.

### Lua syntax, lint, format, and diagnostics

Use Lua 5.1 explicitly and assert the runtime before tests:

```bash
lua -e 'assert(_VERSION == "Lua 5.1", _VERSION)'
luac -v
luacheck --version
```

The first implementation can use the existing syntax and quality suites,
which already extract scripts and use the Mudlet-aware
`tests/test_configs/luacheck_config.lua` configuration.

The durable implementation should add a shared extraction adapter, described
in Phase 3. After that adapter exists:

- `luac -p` is the blocking Lua 5.1 syntax check.
- `luacheck` remains the blocking lint check for undefined globals, suspicious
  assignments, and other Lua quality issues.
- StyLua runs in check-only mode against decoded temporary `.lua` files. It
  must start as report-only, followed by one dedicated formatting change,
  before becoming blocking.
- Lua Language Server runs `--check` with a repository `.luarc.json`, Lua 5.1
  selected, and Mudlet/Geyser definition stubs. Treat this as static
  diagnostics, not a sound type system.
- Type annotations are introduced incrementally for stable project tables and
  functions. Migrating the codebase to Teal or another typed Lua dialect is
  outside this plan.

### Python quality and typing

Add a small, pinned CI tool manifest and configure:

- Ruff linting for `theGUI/*.py`, `scripts/*.py`, and `tests/*.py`.
- Ruff format checking without automatic writes in CI.
- mypy for build and packaging code, introduced incrementally. Start by
  checking `theGUI/build.py` and `theGUI/package.py`, then expand to test tools
  as annotations and dynamic test-result dictionaries are made explicit.
- `python3 -m compileall -q theGUI scripts tests` as a fast syntax guard, with
  `PYTHONPYCACHEPREFIX` pointed inside the job's temporary directory.

Remove the currently tracked root `__pycache__/*.pyc` files before enabling
the clean-worktree assertion. The existing `.gitignore` already excludes
future bytecode. Set `PYTHONDONTWRITEBYTECODE=1` for ordinary Python commands
and redirect explicit compile output so validation never updates a cache in
the checkout.

New checks should be baselined in a dedicated change. Do not suppress whole
rule families merely to make the first run green; use narrow, documented
exceptions for intentional Mudlet or subprocess behavior.

### Build and tests

The blocking test sequence is:

```bash
LUMINARI_CI_TEMP="$(mktemp -d)"
export LUMINARI_CI_TEMP
python3 theGUI/build.py --validate
python3 theGUI/build.py --diff --fail-on-diff
(
  cd tests
  python3 run_tests.py \
    --parallel \
    --report "$LUMINARI_CI_TEMP/test-results.json" \
    --format json
)
python3 scripts/validate_package.py
```

Install Lua 5.1, `luac`, and `luacheck` before running it. Do not pass
`--skip-optional`; a missing quality dependency must fail CI instead of
silently reducing coverage.

The job must finish with a clean worktree. This proves the nominally
read-only commands did not update `build.yaml`, archive files, or generated
XML:

```bash
test -z "$(git status --porcelain --untracked-files=all)"
```

Workflow reports, coverage files, extracted Lua, and scanner output must be
written under the runner's temporary directory and uploaded from there. They
must not require repository ignore rules merely to make the cleanliness check
pass.

Creating a release package is not part of required PR CI. `package.py create`
generates distributable files and should be added only after a dedicated
non-mutating artifact-output mode or an isolated temporary checkout is used.
CI must never invoke `package.py release`.

### Coverage

Publish two independent reports:

1. **Application Lua coverage** measures production Lua actually executed by
   the mock-based tests. Start with the lifecycle regression suite because it
   already executes production scripts under small Mudlet mocks. Use LuaCov
   with stable extracted filenames so reports point back to physical XML
   fragments.
2. **Python tooling coverage** measures the build, package, validation, and test
   orchestration code. Label it as tooling coverage; it does not represent GUI
   coverage.

Coverage is report-only until all of the following are true:

- stable source mapping exists;
- production Lua and generated test snippets are reported separately;
- at least two weeks of `master` baselines are available;
- known Mudlet-only paths can be excluded with documented reasons; and
- the team agrees on thresholds per subsystem.

Do not combine Python and Lua percentages. Do not establish a repository-wide
threshold based mostly on Python test infrastructure. Prefer GitHub job
summaries and retained artifacts initially, avoiding a new hosted coverage
service until it provides clear value.

### Secrets scanning

Run a pinned Gitleaks CLI release rather than depending on an organization
license for the hosted Gitleaks action. Configure it to:

- scan full history on scheduled and `master` runs;
- scan the relevant commit range on pull requests;
- redact detected values from logs;
- emit a machine-readable report artifact; and
- fail on verified findings.

If release metadata checksums or fixtures cause false positives, add only
exact rule, fingerprint, or path-specific allow-list entries in
`.gitleaks.toml`. Never exclude all XML, JSON, Lua, `Releases/`, or source
fragments broadly.

### SAST

Use two complementary scanners:

- CodeQL advanced setup analyzes Python and GitHub Actions. It must not claim
  to analyze application Lua merely because the Lua is stored in `.xml`
  files.
- Semgrep analyzes the stable extracted Lua workspace and can additionally run
  focused XML rules.

Start Semgrep with maintained Lua rules where applicable and add local rules
for LuminariGUI's actual trust boundaries:

- dynamic execution through `load`, `loadstring`, `dofile`, or equivalent;
- shell execution and unsafe process construction;
- untrusted MSDP, trigger, or server text reaching commands or file paths;
- downloads and writes using paths outside the package/profile directory;
- unsafe callback construction or event handler registration;
- unescaped server-controlled content entering HTML/QSS-capable output; and
- accidental logging of credentials, tokens, or private profile data.

Each custom rule needs positive and negative fixtures. New rules should run in
report-only mode until existing findings are triaged, then become blocking for
new violations.

### Dependency and workflow security

Add:

- a human-edited `requirements-ci.in` and generated, pinned
  `requirements-ci.txt` for Python CI tools, including hashes and a documented
  lock-update command;
- `.github/dependabot.yml` entries for `pip` and `github-actions`;
- the dependency review action on pull requests; and
- documented, pinned versions for Lua 5.1, luacheck, LuaCov, StyLua, LuaLS,
  Semgrep, and Gitleaks.

GitHub dependency review does not cover LuaRocks. Lua tools therefore need a
documented scheduled update process and explicit version output in CI logs.

All third-party actions must be pinned to full commit SHAs with a version
comment. Workflows must use minimal permissions, explicit timeouts, and
`concurrency` cancellation for superseded pull-request runs. Do not use
`pull_request_target` for jobs that check out or execute contributor code.
Only CodeQL/SARIF upload jobs should receive `security-events: write`.

## Implementation phases

### Phase 1 — Reproducible core CI

- [x] Remove the tracked root `__pycache__/*.pyc` files; retain the existing
  ignore rules and prevent bytecode writes during CI.
- [x] Add `requirements-ci.in` and a pinned `requirements-ci.txt` for the
  initial Python tools.
- [x] Add `.github/workflows/ci.yml` for pull requests, pushes to `master`, and
  manual dispatch.
- [x] Install and assert Lua 5.1, `luac`, and `luacheck`.
- [x] Run `build.py --validate` and `--diff --fail-on-diff`.
- [x] Run Python compile checks and the initial Ruff checks.
- [x] Run every existing test suite without `--skip-optional`.
- [x] Run `scripts/validate_package.py`.
- [x] Upload the JSON test report on success or failure.
- [x] Assert that the worktree remains unchanged.
- [x] Add job timeouts and cancellation of superseded PR runs.

Implemented 2026-08-05. The initial baseline uses Python 3.12.3, a
hash-locked Ruff/mypy/PyYAML toolchain, Lua 5.1, and luacheck 0.23.0. All
third-party actions are pinned to full commit SHAs. Local verification passed
Ruff, mypy, actionlint 1.7.12, non-mutating assembly/drift validation, all
seven test suites (including lifecycle 33/33), package validation, and the
resource-ownership audit in a clean Ubuntu 24.04 replica. The first hosted
GitHub Actions run, [31044018354](https://github.com/LuminariMUD/LuminariGUI/actions/runs/31044018354),
then passed `quality` in 26 seconds and `build-and-test` in 52 seconds, including
the clean-tree checks and retained JSON report. Phase 1 is accepted.

**Acceptance criteria**

- A malformed fragment, Lua syntax error, failed test, or stale
  `LuminariGUI.xml` makes the appropriate job fail.
- A clean checkout of `master` passes without modifying tracked files.
- Missing Lua or lint tooling fails during setup rather than skipping suites.
- The test report is downloadable from every completed run.

### Phase 2 — Security baseline

- [x] Add a pinned Gitleaks CLI workflow with redacted reports.
- [x] Baseline existing Gitleaks findings with narrow, reviewed exceptions.
- [x] Enable CodeQL advanced setup for Python and GitHub Actions.
- [x] Add the pull-request dependency review workflow.
- [x] Add Dependabot configuration for Python and Actions dependencies.
- [x] Pin action SHAs and declare minimal workflow permissions.
- [x] Add a scheduled weekly full security scan.

Implemented locally 2026-08-05. Gitleaks is checksum-pinned to 8.18.4 because
the current 8.30.1 release has a confirmed false-negative regression; every
run generates a split-string GitHub-token canary, requires it to fail the scan,
and verifies that neither logs nor JSON contain its unredacted value. The
default rules found zero leaks across all 102 existing commits, so
`.gitleaks.toml` contains no exceptions. The workflow adds SHA-pinned CodeQL
4.37.6 for only Python and GitHub Actions, SHA-pinned dependency review 5.0.0,
weekly full scans, and minimal job permissions. Dependabot covers the root pip
lock and GitHub Actions, with matching `dependencies` and `ci` labels created
in the repository. Hosted workflow and deliberately vulnerable PR checks are
pending the checkpoint push.

**Acceptance criteria**

- A generated temporary secret canary makes the scanner fail without exposing
  the value in logs.
- CodeQL produces results for Python and workflow files only.
- Dependency review passes cleanly when no supported dependency changes exist
  and fails for a test PR introducing a known-vulnerable fixture dependency.
- Workflows run safely for forked pull requests without repository secrets.

### Phase 3 — Shared embedded-Lua tool bridge

- [ ] Add `scripts/extract_embedded_lua.py` as a read-only adapter.
- [ ] Read physical sources in `build.yaml` and composite-include order.
- [ ] Extract scripts from scripts, triggers, aliases, and keys exactly once.
- [ ] Decode XML entities while preserving Lua content and stable filenames.
- [ ] Emit a JSON manifest mapping each temporary Lua file to its physical XML
  fragment, Mudlet item name/path, and source location where possible.
- [ ] Reject output-name collisions and traversal outside the temporary root.
- [ ] Add regression tests for entities, empty scripts, duplicate item names,
  composite includes, multiple script elements, and malformed fragments.
- [ ] Refactor existing syntax and quality tests to share the adapter.
- [ ] Add `.luarc.json` and versioned Mudlet/Geyser definition stubs.
- [ ] Add LuaLS diagnostics in report-only mode, then establish a blocking
  severity policy.
- [ ] Add `.stylua.toml` and a report-only format check; perform a dedicated
  formatting baseline before enforcing it.
- [ ] Add Semgrep Lua rules and fixtures, initially report-only.

**Acceptance criteria**

- The adapter extracts every non-empty Lua script that the build assembles,
  with no duplicates or missing fragments.
- Diagnostics name the originating XML fragment and Mudlet item rather than a
  random temporary filename.
- The adapter never rewrites source files or generated XML.
- LuaLS, StyLua, luacheck, Semgrep, and LuaCov consume the same extracted
  representation.

### Phase 4 — Coverage and test reporting

- [ ] Instrument production Lua executed by lifecycle and other mock-based
  tests with LuaCov.
- [ ] Exclude generated snippets from production coverage or report them in a
  separate category.
- [ ] Add coverage tests for the extractor and the Python build/package tools.
- [ ] Produce separate Lua and Python HTML plus machine-readable reports.
- [ ] Add concise coverage deltas to the GitHub job summary.
- [ ] Retain raw reports as workflow artifacts.
- [ ] Collect baseline history before proposing subsystem thresholds.
- [ ] Document every exclusion and the Mudlet runtime behavior it represents.

**Acceptance criteria**

- Every reported Lua path maps to a tracked XML fragment.
- Python and Lua totals remain visibly separate.
- Coverage collection does not change runtime behavior or test outcomes.
- No coverage threshold is required until the baseline review is complete.

### Phase 5 — Mudlet runtime smoke testing

- [ ] Preserve a manual release checklist for Mudlet 4.22 or the current
  documented supported release.
- [ ] Cover package import, connection, MSDP subscription and updates, map
  initialization, tab/callback interaction, `fix gui`, reconnect,
  `resetProfile()`, resize behavior, and package replacement.
- [ ] Investigate an opt-in Linux/Xvfb smoke job using an official Mudlet
  build; keep it non-blocking until it is reliable.
- [ ] Capture Mudlet logs and screenshots when an automated smoke run fails.
- [ ] Keep platform-specific Qt/Geyser visual checks manual unless automation
  proves stable across supported platforms.

**Acceptance criteria**

- The release checklist distinguishes package failures from documented Mudlet
  regressions in `docs/MUDLET_COMPATIBILITY.md`.
- Automated smoke results are not required until flake rate and environment
  setup are acceptable.
- A release is never approved solely from mocked test or coverage results.

### Phase 6 — Enforcement and documentation

- [ ] Require stable quality, build/test, Gitleaks, CodeQL, Semgrep, and
  dependency-review checks through branch protection.
- [ ] Keep coverage and experimental Mudlet smoke checks informational until
  their phase-specific criteria are met.
- [ ] Update `AGENTS.md`, `CONTRIBUTING.md`, and `docs/PYTHON_TOOLS.md` with
  exact local equivalents of required CI checks.
- [ ] Add troubleshooting for tool installation, Lua version mismatch,
  source-map errors, and false-positive review.
- [ ] Add a CI status badge only after required check names are stable.
- [ ] Record tool owners, update cadence, and expected artifact retention.

**Acceptance criteria**

- Contributors can reproduce every blocking check locally.
- Required check names remain stable and are documented.
- All actions and scanners are pinned and covered by an update process.
- The central project task list links to this plan until completion.

## Recommended pull-request job order

Jobs should run in parallel where safe:

1. `quality` and `gitleaks` start immediately.
2. `build-and-test` starts immediately using the same pinned tool versions.
3. `codeql` and `dependency-review` start independently.
4. `semgrep-lua` depends only on the extraction adapter setup, not on tests.
5. `coverage` may depend on `build-and-test` or run as a separate non-blocking
   job if duplication remains inexpensive.

Use caches only for immutable package downloads and keyed dependency installs.
Do not cache generated XML, extracted Lua, test results, or security reports.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| CI accidentally increments the package version | Permit only `--validate` and `--diff --fail-on-diff`; finish with a clean `git status --porcelain` assertion |
| Python imports rewrite tracked or local bytecode | Remove tracked `.pyc` files, disable routine bytecode writes, and redirect compile output to the job temp directory |
| Runner uses Lua 5.4 instead of Mudlet-compatible Lua | Install Lua 5.1 explicitly and assert `_VERSION` before tests |
| Lua tools report random temporary paths | Use one stable extraction adapter and emit a source-map manifest |
| Mudlet globals produce unusable lint/type noise | Reuse luacheck globals and maintain narrow versioned Mudlet/Geyser stubs |
| Formatter changes XML or decoded Lua semantics | Run check-only on temporary Lua; baseline formatting separately; never reserialize XML in CI |
| CodeQL creates a false sense of Lua coverage | Label CodeQL jobs Python/Actions and use Semgrep plus custom Lua rules |
| Coverage overstates GUI confidence | Separate Lua/Python reports and retain a Mudlet runtime release gate |
| Dependency review appears green with no manifests | Add pinned Python CI manifests and document the LuaRocks coverage gap |
| Security scanners flag checksums or fixtures | Use exact reviewed allow-list entries; never exclude broad source paths |
| Third-party action or tool drift breaks CI | Pin actions to SHAs and tools to versions; use Dependabot plus scheduled review |
| Forked PRs gain excessive permissions | Avoid `pull_request_target`, use minimal permissions, and never expose secrets to contributor code |

## Definition of done

The project reaches the intended comprehensive baseline when:

- all source fragments and generated XML are validated without mutations;
- Lua 5.1 syntax and Mudlet-aware lint checks are mandatory;
- the full existing test suite runs with no optional suites skipped;
- Python lint, format, and agreed typing checks are reproducible locally;
- LuaLS and Semgrep analyze stable extracted production scripts;
- Gitleaks, CodeQL, and dependency review protect pull requests;
- Lua and Python coverage are published separately and accurately labeled;
- branch protection requires every stable blocking job;
- scheduled scans and dependency updates are active; and
- real Mudlet smoke testing remains part of release verification.

## References

- [Build and validation commands](../../theGUI/build.py)
- [Current test runner](../../tests/run_tests.py)
- [Mudlet-aware luacheck configuration](../../tests/test_configs/luacheck_config.lua)
- [Mudlet compatibility and runtime test guidance](../MUDLET_COMPATIBILITY.md)
- [GitHub CodeQL supported languages](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning)
- [GitHub dependency graph ecosystems](https://docs.github.com/en/code-security/reference/supply-chain-security/dependency-graph-supported-package-ecosystems)
- [Lua Language Server diagnosis reports](https://luals.github.io/wiki/diagnosis-report/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Semgrep language support](https://github.com/semgrep/semgrep)
