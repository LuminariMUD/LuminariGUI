#!/usr/bin/env python3
"""
Lifecycle regression tests for upgrade/reset handling and the build drift guard.

These tests execute the relevant Lua directly from the source fragment with
small Mudlet mocks, so they fail if the production handler logic regresses.
"""

import html
import shutil
import subprocess
import sys
import tempfile
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
