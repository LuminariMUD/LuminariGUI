#!/usr/bin/env python3
"""
Regression tests for Mudlet lifecycle handling and the Python tooling.

The lifecycle cases execute production Lua with small Mudlet mocks. Tooling
cases use isolated project copies (and a temporary Git repository for release)
so versioning, packaging, and drift checks are exercised without mutating the
working tree.
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


class LifecycleRegressionTester:
    def __init__(self, _xml_file=None):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.gui_source_path = self.repo_root / "theGUI" / "src" / "scripts" / "01_gui.xml"
        self.mapper_source_path = (
            self.repo_root / "theGUI" / "src" / "scripts" / "00_msdpmapper.xml"
        )
        self.lua_path = self._find_lua()
        self.test_results = []
        self.errors = []
        self.warnings = []

    @staticmethod
    def _find_lua():
        for executable in ("lua", "lua5.1", "lua5.2", "lua5.3", "lua5.4", "luajit"):
            path = shutil.which(executable)
            if path:
                return path
        return None

    @staticmethod
    def _extract(source, start_marker, end_marker):
        start = source.index(start_marker)
        end = source.index(end_marker, start)
        return html.unescape(source[start:end])

    def _run_lua(self, script):
        result = subprocess.run(
            [self.lua_path, "-"],
            input=script,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise AssertionError(detail or f"Lua exited with {result.returncode}")

    @staticmethod
    def _require(condition, message):
        if not condition:
            raise AssertionError(message)

    def _test_upgrade_preserves_file_scope_handler_ids(self):
        source = self.gui_source_path.read_text(encoding="utf-8")
        register_function = self._extract(
            source,
            "function GUI.registerEventHandlers()",
            "\n-- =============================================================================\n"
            "-- CENTRALIZED GUI INITIALIZATION SYSTEM",
        )

        script = f'''
GUI = {{
  eventHandlerIds = {{
    shiftRoom = 101,
    sysConnectionEvent = 102,
    sysDownloadDone = 103,
    sysProtocolEnabled = 104,
    ["msdp.ROOM_map"] = 105,
    ["sysProtocolEnabled_map"] = 106,
    ["msdp.HEALTH"] = 201,
  }}
}}
msdp = {{}}
demonnic = {{chat = {{use = false}}}}
killed = {{}}
next_id = 300

function killAnonymousEventHandler(id)
  killed[id] = true
  return true
end

function registerAnonymousEventHandler()
  next_id = next_id + 1
  return next_id
end

function tempTimer() end

{register_function}

GUI.registerEventHandlers()

for _, id in ipairs({{101, 102, 103, 104, 105, 106}}) do
  assert(not killed[id], "killed shared file-scope handler " .. id)
end
assert(killed[201], "did not clean the owned GUI handler")
assert(GUI.eventHandlerIds.shiftRoom == 101)
assert(GUI.eventHandlerIds.sysProtocolEnabled == 104)
assert(GUI.eventHandlerIds["msdp.ROOM_map"] == 105)
assert(GUI.eventHandlerIds["msdp.HEALTH"] ~= 201)
'''
        self._run_lua(script)

    def _test_mapper_initializer_is_exported(self):
        source = self.mapper_source_path.read_text(encoding="utf-8")
        self._require(
            "function map.initialize()" in source,
            "mapper initializer is not exported as map.initialize",
        )
        self._require(
            "local function config()" not in source,
            "mapper setup is still private to the mapper script",
        )

    def _test_profile_reset_initializes_mapper(self):
        source = self.gui_source_path.read_text(encoding="utf-8")
        reset_handler = self._extract(
            source,
            'registerAnonymousEventHandler("sysLoadEvent", function(_, isNewLoad)',
            '\nregisterAnonymousEventHandler("sysInstall"',
        )

        script = f'''
calls = {{gui = 0, mapper = 0, reports = 0, refresh = 0}}
handlers = {{}}

function registerAnonymousEventHandler(event, handler)
  handlers[event] = handler
end

function tempTimer(_, callback)
  callback()
end

GUI = {{
  init = function() calls.gui = calls.gui + 1 end,
  requestMSDPReports = function()
    calls.reports = calls.reports + 1
    return true
  end,
  initializeOrRefresh = function() calls.refresh = calls.refresh + 1 end,
}}

map = {{
  initialize = function()
    calls.mapper = calls.mapper + 1
    return true
  end,
}}

{reset_handler}

handlers.sysLoadEvent("sysLoadEvent", false)
assert(calls.gui == 1)
assert(calls.mapper == 1, "mapper was not initialized after resetProfile()")
assert(calls.reports == 1)
assert(calls.refresh == 1)

handlers.sysLoadEvent("sysLoadEvent", true)
assert(calls.gui == 2)
assert(calls.mapper == 1, "reset recovery ran during a fresh profile load")
'''
        self._run_lua(script)

    def _copy_build_tree(self, destination):
        project_root = destination / "project"
        shutil.copytree(self.repo_root / "theGUI", project_root / "theGUI")
        return project_root

    @staticmethod
    def _run_build_check(project_root, *arguments):
        return subprocess.run(
            [sys.executable, str(project_root / "theGUI" / "build.py"), *arguments],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

    @staticmethod
    def _run_package(project_root, *arguments, environment=None):
        return subprocess.run(
            [sys.executable, str(project_root / "theGUI" / "package.py"), *arguments],
            cwd=project_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )

    @staticmethod
    def _manifest_version(project_root):
        content = (project_root / "theGUI" / "build.yaml").read_text(encoding="utf-8")
        match = re.search(r'version:\s*"([^"]+)"', content)
        if not match:
            raise AssertionError("build.yaml has no version")
        return match.group(1)

    @staticmethod
    def _xml_version(xml_path):
        return ET.parse(xml_path).getroot().attrib.get("version")

    @staticmethod
    def _next_version(version):
        parts = version.split(".")
        width = len(parts[-1])
        try:
            parts[-1] = str(int(parts[-1]) + 1).zfill(width)
        except ValueError:
            parts.append("1")
        return ".".join(parts)

    def _assert_package_versions(self, project_root, expected_version):
        package_path = (
            project_root / "Releases" / f"LuminariGUI-v{expected_version}.mpackage"
        )
        self._require(package_path.exists(), f"missing package {package_path.name}")
        self._require(
            self._manifest_version(project_root) == expected_version,
            "build.yaml version does not match package version",
        )
        self._require(
            self._xml_version(project_root / "LuminariGUI.xml") == expected_version,
            "built XML version does not match package version",
        )

        with zipfile.ZipFile(package_path) as package:
            config = package.read("config.lua").decode("utf-8")
            packaged_xml = ET.fromstring(package.read("LuminariGUI.xml"))

        self._require(
            f'version = "{expected_version}"' in config,
            "config.lua version does not match package version",
        )
        self._require(
            packaged_xml.attrib.get("version") == expected_version,
            "packaged XML version does not match package version",
        )

    def _test_create_version_override_is_consistent(self):
        with tempfile.TemporaryDirectory(prefix="luminari-package-version-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            target_version = "9.8.7.006"

            result = self._run_package(
                project_root,
                "create",
                "--version",
                target_version,
                "--skip-tests",
            )

            self._require(result.returncode == 0, result.stdout + result.stderr)
            self._assert_package_versions(project_root, target_version)

    def _test_create_default_version_is_consistent(self):
        with tempfile.TemporaryDirectory(prefix="luminari-package-version-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            expected_version = self._next_version(
                self._manifest_version(project_root)
            )

            result = self._run_package(
                project_root,
                "create",
                "--skip-tests",
            )

            self._require(result.returncode == 0, result.stdout + result.stderr)
            self._assert_package_versions(project_root, expected_version)

    def _test_skip_build_rejects_version_mismatch(self):
        with tempfile.TemporaryDirectory(prefix="luminari-package-version-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            shutil.copy2(
                self.repo_root / "LuminariGUI.xml",
                project_root / "LuminariGUI.xml",
            )

            result = self._run_package(
                project_root,
                "create",
                "--version",
                "9.8.7.006",
                "--skip-build",
                "--skip-tests",
            )

            self._require(result.returncode == 1, result.stdout + result.stderr)
            self._require(
                "Refusing to package mismatched versions" in result.stdout,
                "skip-build mismatch did not explain why packaging was refused",
            )

    def _run_release_build_probe(self, project_root, override, expected_version):
        probe = r'''
import importlib.util
import sys

module_path, current_version, override, expected = sys.argv[1:]
spec = importlib.util.spec_from_file_location("luminari_package_probe", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

requested = None if override == "-" else override
workflow = module.ReleaseWorkflow(
    requested or current_version,
    version_override=requested,
)
assert workflow.run_build()
assert workflow.version == expected, (workflow.version, expected)
assert workflow.packager.version == expected
assert module.get_version_from_build_yaml() == expected
assert module.get_version_from_xml(module.PROJECT_ROOT / "LuminariGUI.xml") == expected
'''
        current_version = self._manifest_version(project_root)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                probe,
                str(project_root / "theGUI" / "package.py"),
                current_version,
                override or "-",
                expected_version,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self._require(result.returncode == 0, result.stdout + result.stderr)

    def _test_release_build_version_is_consistent(self):
        with tempfile.TemporaryDirectory(prefix="luminari-release-version-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            expected_version = self._next_version(
                self._manifest_version(project_root)
            )
            self._run_release_build_probe(project_root, None, expected_version)

        with tempfile.TemporaryDirectory(prefix="luminari-release-version-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            self._run_release_build_probe(project_root, "9.8.7.006", "9.8.7.006")

    def _test_release_checks_git_before_build(self):
        probe = r'''
import importlib.util
import sys

module_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("luminari_release_order_probe", module_path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

calls = []
workflow = module.ReleaseWorkflow("2.0.4.028")
workflow.check_git_status = lambda: calls.append("git") or True
workflow.check_github_access = lambda: calls.append("github_access") or True
workflow.run_build = lambda: calls.append("build") or True
workflow.run_tests = lambda: calls.append("tests") or True
workflow.create_release_branch = lambda: calls.append("branch") or True
workflow.create_package = lambda: calls.append("package") or True
workflow.create_tag_merge_and_publish = lambda: calls.append("publish") or True
workflow.publish_github_release = lambda: calls.append("github") or True
assert workflow.execute()
assert calls == [
    "git", "github_access", "build", "tests", "branch", "package", "publish",
    "github"
], calls
'''
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                probe,
                str(self.repo_root / "theGUI" / "package.py"),
            ],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self._require(result.returncode == 0, result.stdout + result.stderr)

    @staticmethod
    def _run_git(project_root, *arguments):
        return subprocess.run(
            ["git", *arguments],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def _test_release_command_end_to_end(self):
        with tempfile.TemporaryDirectory(prefix="luminari-release-e2e-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            shutil.copy2(
                self.repo_root / "LuminariGUI.xml",
                project_root / "LuminariGUI.xml",
            )

            current_version = self._manifest_version(project_root)
            expected_version = self._next_version(current_version)
            setup_commands = [
                ("init",),
                ("branch", "-M", "master"),
                ("config", "user.name", "LuminariGUI Tests"),
                ("config", "user.email", "tests@example.invalid"),
                ("add", "."),
                ("commit", "-m", "Initial test fixture"),
            ]
            for command in setup_commands:
                setup = self._run_git(project_root, *command)
                self._require(
                    setup.returncode == 0,
                    setup.stdout + setup.stderr,
                )

            remote_path = Path(temp_dir) / "origin.git"
            remote_init = self._run_git(
                project_root,
                "init",
                "--bare",
                str(remote_path),
            )
            self._require(
                remote_init.returncode == 0,
                remote_init.stdout + remote_init.stderr,
            )
            remote_add = self._run_git(
                project_root,
                "remote",
                "add",
                "origin",
                str(remote_path),
            )
            self._require(
                remote_add.returncode == 0,
                remote_add.stdout + remote_add.stderr,
            )

            fake_bin = Path(temp_dir) / "bin"
            fake_bin.mkdir()
            gh_log = Path(temp_dir) / "gh.log"
            fake_gh = fake_bin / "gh"
            fake_gh.write_text(
                f"""#!/usr/bin/env python3
import json
import sys
from pathlib import Path

arguments = sys.argv[1:]
with Path({str(gh_log)!r}).open("a", encoding="utf-8") as log:
    log.write(json.dumps(arguments) + "\\n")

if arguments[:2] == ["auth", "status"]:
    raise SystemExit(0)

if arguments[:2] == ["release", "create"]:
    tag = arguments[2]
    print(f"https://example.invalid/releases/tag/{{tag}}")
    raise SystemExit(0)

if arguments[:2] == ["release", "view"]:
    tag = arguments[2]
    version = tag.removeprefix("v")
    print(json.dumps({{
        "url": f"https://example.invalid/releases/tag/{{tag}}",
        "isDraft": False,
        "isPrerelease": False,
        "tagName": tag,
        "assets": [
            {{
                "name": f"LuminariGUI-v{{version}}.mpackage",
                "state": "uploaded",
            }},
            {{
                "name": f"LuminariGUI-v{{version}}.json",
                "state": "uploaded",
            }},
        ],
    }}))
    raise SystemExit(0)

print("unexpected gh invocation", file=sys.stderr)
raise SystemExit(1)
""",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = (
                str(fake_bin)
                + os.pathsep
                + environment.get("PATH", "")
            )

            result = self._run_package(
                project_root,
                "release",
                "--skip-tests",
                environment=environment,
            )
            self._require(result.returncode == 0, result.stdout + result.stderr)
            self._require(
                "Published master, "
                f"release/v{expected_version}, and v{expected_version} to origin"
                in result.stdout,
                "release did not report verified publication",
            )
            self._require(
                f"Release v{expected_version} fully published and verified!"
                in result.stdout,
                "release did not report publication as its terminal state",
            )
            gh_calls = [
                json.loads(line)
                for line in gh_log.read_text(encoding="utf-8").splitlines()
            ]
            self._require(
                any(call[:2] == ["release", "create"] for call in gh_calls),
                "release did not create the GitHub Release",
            )
            self._require(
                any(call[:2] == ["release", "view"] for call in gh_calls),
                "release did not verify the GitHub Release",
            )
            self._assert_package_versions(project_root, expected_version)

            branch = self._run_git(project_root, "branch", "--show-current")
            self._require(branch.returncode == 0, branch.stdout + branch.stderr)
            self._require(
                branch.stdout.strip() == "master",
                f"release finished on unexpected branch: {branch.stdout!r}",
            )

            tag = self._run_git(
                project_root,
                "rev-parse",
                "--verify",
                f"refs/tags/v{expected_version}",
            )
            self._require(tag.returncode == 0, tag.stdout + tag.stderr)

            refs = (
                ("refs/heads/master", "refs/heads/master"),
                (
                    f"refs/heads/release/v{expected_version}",
                    f"refs/heads/release/v{expected_version}",
                ),
                (
                    f"refs/tags/v{expected_version}",
                    f"refs/tags/v{expected_version}",
                ),
            )
            for local_ref, remote_ref in refs:
                local = self._run_git(project_root, "rev-parse", local_ref)
                self._require(local.returncode == 0, local.stdout + local.stderr)
                remote = self._run_git(
                    project_root,
                    "ls-remote",
                    "--exit-code",
                    "origin",
                    remote_ref,
                )
                self._require(remote.returncode == 0, remote.stdout + remote.stderr)
                remote_sha = remote.stdout.split()[0] if remote.stdout else ""
                self._require(
                    remote_sha == local.stdout.strip(),
                    f"{remote_ref} was not pushed at the local release SHA",
                )

            master_tree = self._run_git(
                project_root,
                "ls-tree",
                "-r",
                "--name-only",
                "master",
            )
            self._require(
                master_tree.returncode == 0,
                master_tree.stdout + master_tree.stderr,
            )
            self._require(
                f"Releases/LuminariGUI-v{expected_version}.mpackage"
                in master_tree.stdout,
                "release package was not committed and merged to master",
            )
            self._require(
                f"docs/archive/LuminariGUI.xml_{current_version}"
                in master_tree.stdout,
                "generated archive was not committed and merged to master",
            )

            status = self._run_git(project_root, "status", "--porcelain")
            self._require(status.returncode == 0, status.stdout + status.stderr)
            self._require(
                status.stdout == "",
                f"release left the repository dirty: {status.stdout!r}",
            )

    def _test_runner_output_flags(self):
        base_command = [
            sys.executable,
            str(self.repo_root / "tests" / "run_tests.py"),
            "--xml",
            str(self.repo_root / "LuminariGUI.xml"),
            "--test",
            "functions",
        ]

        quiet = subprocess.run(
            [*base_command, "--quiet"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self._require(quiet.returncode == 0, quiet.stdout + quiet.stderr)
        self._require(
            quiet.stdout.strip() == "PASS: 1/1 test suites",
            f"quiet output was not concise: {quiet.stdout!r}",
        )

        verbose = subprocess.run(
            [*base_command, "--verbose"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self._require(verbose.returncode == 0, verbose.stdout + verbose.stderr)
        self._require(
            "Runner configuration:" in verbose.stdout,
            "verbose output did not include runner configuration",
        )

    def _test_missing_optional_dependency_is_failure(self):
        luac_path = shutil.which("luac")
        self._require(luac_path is not None, "luac is required for this regression test")

        with tempfile.TemporaryDirectory(prefix="luminari-test-tools-") as temp_dir:
            tool_dir = Path(temp_dir)
            (tool_dir / "lua").symlink_to(self.lua_path)
            (tool_dir / "luac").symlink_to(luac_path)
            environment = os.environ.copy()
            environment["PATH"] = str(tool_dir)

            result = subprocess.run(
                [
                    sys.executable,
                    str(self.repo_root / "tests" / "run_tests.py"),
                    "--xml",
                    str(self.repo_root / "LuminariGUI.xml"),
                    "--sequential",
                ],
                cwd=self.repo_root,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )

        self._require(result.returncode == 1, result.stdout + result.stderr)
        self._require(
            "Missing dependencies: luacheck" in result.stdout,
            "missing luacheck was not reported",
        )
        self._require(
            "Running Lua Syntax" not in result.stdout,
            "test suites ran despite the dependency hard failure",
        )

    def _test_guard_fails_read_only_when_output_is_missing(self):
        with tempfile.TemporaryDirectory(prefix="luminari-build-guard-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            config_path = project_root / "theGUI" / "build.yaml"
            config_before = config_path.read_bytes()

            result = self._run_build_check(project_root, "--fail-on-diff")

            self._require(result.returncode == 1, result.stdout + result.stderr)
            self._require(
                config_path.read_bytes() == config_before,
                "missing-output guard changed build.yaml",
            )
            self._require(
                not (project_root / "LuminariGUI.xml").exists(),
                "missing-output guard created LuminariGUI.xml",
            )
            self._require(
                not (project_root / "docs" / "archive").exists(),
                "missing-output guard created an archive",
            )

    def _test_guard_fails_read_only_when_output_is_stale(self):
        with tempfile.TemporaryDirectory(prefix="luminari-build-guard-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            config_path = project_root / "theGUI" / "build.yaml"
            output_path = project_root / "LuminariGUI.xml"
            output_path.write_text("stale output\n", encoding="utf-8")
            config_before = config_path.read_bytes()
            output_before = output_path.read_bytes()

            result = self._run_build_check(project_root, "--fail-on-diff")

            self._require(result.returncode == 1, result.stdout + result.stderr)
            self._require(
                config_path.read_bytes() == config_before,
                "stale-output guard changed build.yaml",
            )
            self._require(
                output_path.read_bytes() == output_before,
                "stale-output guard rewrote LuminariGUI.xml",
            )
            self._require(
                not (project_root / "docs" / "archive").exists(),
                "stale-output guard created an archive",
            )

    def _test_diff_is_read_only_and_informational(self):
        with tempfile.TemporaryDirectory(prefix="luminari-build-guard-") as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            config_path = project_root / "theGUI" / "build.yaml"
            output_path = project_root / "LuminariGUI.xml"
            output_path.write_text("stale output\n", encoding="utf-8")
            config_before = config_path.read_bytes()
            output_before = output_path.read_bytes()

            result = self._run_build_check(project_root, "--diff")

            self._require(result.returncode == 0, result.stdout + result.stderr)
            self._require(
                config_path.read_bytes() == config_before,
                "informational diff changed build.yaml",
            )
            self._require(
                output_path.read_bytes() == output_before,
                "informational diff rewrote LuminariGUI.xml",
            )
            self._require(
                not (project_root / "docs" / "archive").exists(),
                "informational diff created an archive",
            )

    def _test_guard_accepts_synced_output_without_mutation(self):
        config_path = self.repo_root / "theGUI" / "build.yaml"
        output_path = self.repo_root / "LuminariGUI.xml"
        archive_path = self.repo_root / "docs" / "archive"
        config_before = config_path.read_bytes()
        output_before = output_path.read_bytes()
        archives_before = sorted(path.name for path in archive_path.iterdir())

        result = self._run_build_check(self.repo_root, "--fail-on-diff")

        self._require(result.returncode == 0, result.stdout + result.stderr)
        self._require(
            config_path.read_bytes() == config_before,
            "synced-output guard changed build.yaml",
        )
        self._require(
            output_path.read_bytes() == output_before,
            "synced-output guard rewrote LuminariGUI.xml",
        )
        self._require(
            sorted(path.name for path in archive_path.iterdir()) == archives_before,
            "synced-output guard changed the archive set",
        )

    def run_tests(self):
        print("Running lifecycle regression tests...")

        if not self.lua_path:
            self.errors.append("lua interpreter not found in PATH")
            print("  ✗ Lua is required for lifecycle regression tests")
            return False

        tests = [
            (
                "upgrade_handler_ownership",
                self._test_upgrade_preserves_file_scope_handler_ids,
            ),
            ("mapper_initializer_exported", self._test_mapper_initializer_is_exported),
            ("profile_reset_mapper", self._test_profile_reset_initializes_mapper),
            (
                "guard_missing_output",
                self._test_guard_fails_read_only_when_output_is_missing,
            ),
            (
                "guard_stale_output",
                self._test_guard_fails_read_only_when_output_is_stale,
            ),
            ("informational_diff", self._test_diff_is_read_only_and_informational),
            (
                "guard_synced_output",
                self._test_guard_accepts_synced_output_without_mutation,
            ),
            (
                "create_version_override",
                self._test_create_version_override_is_consistent,
            ),
            (
                "create_default_version",
                self._test_create_default_version_is_consistent,
            ),
            (
                "skip_build_version_mismatch",
                self._test_skip_build_rejects_version_mismatch,
            ),
            (
                "release_build_version",
                self._test_release_build_version_is_consistent,
            ),
            (
                "release_preflight_order",
                self._test_release_checks_git_before_build,
            ),
            ("release_end_to_end", self._test_release_command_end_to_end),
            ("runner_output_flags", self._test_runner_output_flags),
            (
                "missing_optional_dependency_failure",
                self._test_missing_optional_dependency_is_failure,
            ),
        ]

        for name, test in tests:
            try:
                test()
                self.test_results.append({"name": name, "success": True})
                print(f"  ✓ {name}")
            except Exception as error:
                message = f"{name}: {error}"
                self.errors.append(message)
                self.test_results.append(
                    {"name": name, "success": False, "error": str(error)}
                )
                print(f"  ✗ {message}")

        passed = sum(result["success"] for result in self.test_results)
        print(f"Lifecycle regression results: {passed}/{len(tests)} passed")
        return passed == len(tests)

    def get_results(self):
        return {
            "test_results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    tester = LifecycleRegressionTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
