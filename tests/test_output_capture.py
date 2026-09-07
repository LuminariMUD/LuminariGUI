#!/usr/bin/env python3
"""Regression tests for boundary-driven ASCII map capture and output spacing."""

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class OutputCaptureTester:
    def __init__(self, _xml_file=None):
        self.repo_root = PROJECT_ROOT
        self.capture_path = (
            self.repo_root
            / "theGUI"
            / "src"
            / "scripts"
            / "gui"
            / "37_ascii_map_capture.xml"
        )
        self.trigger_path = (
            self.repo_root / "theGUI" / "src" / "triggers" / "01_gui.xml"
        )
        self.lua_path = self._find_lua()
        self.test_results = []
        self.errors = []
        self.warnings = []
        self.capture_source = self._capture_source()

    @staticmethod
    def _find_lua():
        for executable in ("lua", "lua5.1", "lua5.2", "lua5.3", "lua5.4", "luajit"):
            path = shutil.which(executable)
            if path:
                return path
        return None

    def _capture_source(self):
        fragment = ET.fromstring(
            "<root>" + self.capture_path.read_text(encoding="utf-8") + "</root>"
        )
        scripts = fragment.findall(".//Script")
        if len(scripts) != 1 or scripts[0].findtext("name") != "ASCII Map Capture":
            raise AssertionError("ASCII map capture fragment has unexpected topology")
        return scripts[0].findtext("script") or ""

    @staticmethod
    def _mocks():
        return r"""
destination = {}
destinationStyles = {}
main = {}
deletedLines = {}
debugEvents = {}
fitCalls = {}
timers = {}
activeTriggers = {[77] = true}
nextTimerId = 100
currentLine = nil
currentStyle = nil
copiedLine = nil
copiedStyle = nil
pendingPrefix = ""
failAppend = false
throwAppend = false
failClear = false
failDelete = false
clearCount = 0

local function container()
  return {
    shown = 0,
    hidden = 0,
    show = function(self) self.shown = self.shown + 1 end,
    hide = function(self) self.hidden = self.hidden + 1 end,
  }
end

GUI = {
  buttonWindow = {mudletOrAscii = "ASCII"},
  asciiMapContainer = container(),
  debug = function(scope, message, detail)
    debugEvents[#debugEvents + 1] = {scope = scope, message = message, detail = detail}
  end,
  debugError = function(scope, message)
    debugEvents[#debugEvents + 1] = {scope = scope, message = message, error = true}
  end,
}

function GUI.cancelOwnedTimer(name)
  local present = timers[name] ~= nil
  timers[name] = nil
  return present
end

function GUI.setOwnedTimer(name, delay, callback)
  GUI.cancelOwnedTimer(name)
  nextTimerId = nextTimerId + 1
  timers[name] = {id = nextTimerId, delay = delay, callback = callback}
  return nextTimerId
end

function fireTimer(name)
  local timer = timers[name]
  assert(timer, "timer does not exist: " .. tostring(name))
  timers[name] = nil
  timer.callback()
end

map = {
  maplineTrig = 77,
  container = container(),
  minimap = {},
  calcMinimapPadding = function() return 2.9 end,
  adjustAsciimapFontSize = function(columns, rows)
    fitCalls[#fitCalls + 1] = {kind = "room", columns = columns, rows = rows}
  end,
  adjustMinimapFontSize = function(columns, rows)
    fitCalls[#fitCalls + 1] = {kind = "wilderness", columns = columns, rows = rows}
  end,
}

function map.minimap:echo(value)
  if value:sub(-1) == "\n" then
    destination[#destination + 1] = pendingPrefix .. value:sub(1, -2)
    destinationStyles[#destinationStyles + 1] = nil
    pendingPrefix = ""
  else
    pendingPrefix = pendingPrefix .. value
  end
end

function exists(itemId, itemType)
  if itemType == "trigger" and activeTriggers[itemId] then return 1 end
  return 0
end

function killTrigger(itemId)
  if not activeTriggers[itemId] then return false end
  activeTriggers[itemId] = nil
  return true
end

function clearUserWindow(name)
  assert(name == "map.minimap")
  if failClear then return false end
  destination = {}
  destinationStyles = {}
  pendingPrefix = ""
  clearCount = clearCount + 1
end

function selectCurrentLine()
  assert(currentLine ~= nil)
end

function copy()
  copiedLine = currentLine
  copiedStyle = currentStyle
end

function appendBuffer(name)
  assert(name == "map.minimap")
  if throwAppend then error("append failure") end
  if failAppend then return false end
  destination[#destination + 1] = pendingPrefix .. copiedLine
  destinationStyles[#destinationStyles + 1] = copiedStyle
  pendingPrefix = ""
end

function deleteLine()
  if failDelete then error("delete failure") end
  deletedLines[#deletedLines + 1] = currentLine
end

function feedLine(text, style)
  currentLine = text
  currentStyle = style
  local deletedBefore = #deletedLines
  local action = GUI.AsciiMapCapture.processLine(text)
  if #deletedLines == deletedBefore then
    main[#main + 1] = {text = text, style = style}
  end
  return action
end

function repeatedRow(width, symbol)
  assert(#symbol == 1)
  return symbol .. string.rep(" ", width - 1)
end
"""

    def _run_lua(self, body):
        source = self._mocks() + "\n" + self.capture_source + "\n" + body
        result = subprocess.run(
            [self.lua_path, "-"],
            input=source,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise AssertionError((result.stderr or result.stdout).strip())

    def _test_permanent_trigger_and_spacing_contract(self):
        root = ET.fromstring(
            "<root>" + self.trigger_path.read_text(encoding="utf-8") + "</root>"
        )
        gui = next(
            node
            for node in root.findall("./TriggerGroup")
            if node.findtext("name") == "GUI"
        )
        triggers = gui.findall("./Trigger")
        capture = [
            node for node in triggers if node.findtext("name") == "Capture ASCII Maps"
        ]
        if len(capture) != 1:
            raise AssertionError("exactly one permanent ASCII map trigger is required")
        if capture[0].findtext("regexCodeList/string") != "^.*$":
            raise AssertionError(
                "ASCII map trigger does not dispatch every logical line"
            )
        if capture[0].get("isTempTrigger") != "no":
            raise AssertionError("ASCII map dispatcher unexpectedly became temporary")

        source = self.trigger_path.read_text(encoding="utf-8")
        forbidden = (
            "Gag blank lines",
            "Capture Room Map",
            "Capture Wilderness Map",
            "tempLineTrigger(1,11",
            "tempLineTrigger(1,23",
            "function onRoomMapLine",
            "function onMapLine",
        )
        returned = [value for value in forbidden if value in source]
        if returned:
            raise AssertionError(
                "obsolete output triggers returned: " + ", ".join(returned)
            )

        self._run_lua(
            r"""
assert(map.maplineTrig == nil, "legacy line trigger ID survived parser load")
assert(activeTriggers[77] == nil, "legacy line trigger survived parser load")
assert(feedLine("ordinary output") == "ignored")
assert(feedLine("") == "ignored")
assert(feedLine("   indented   words   ") == "ignored")
assert(#deletedLines == 0, "ordinary output was deleted")
assert(#main == 3 and main[2].text == "" and main[3].text == "   indented   words   ")
"""
        )

    def _test_exact_room_fixture_and_formatting(self):
        self._run_lua(
            r"""
local rows = {
  "    [.]-[|]-[.]    ",
  "         |         ",
  "    [.]-[C]-[.] [.]",
  "         |       | ",
  "    [.]-[&]-[.] [Y]",
  "         |       | ",
  "    [.]-[C]-[,]-[Y]",
  "         |   |     ",
  "[-]-[-]-[,]-[,]-[.]",
}

assert(feedLine("before") == "ignored")
assert(feedLine("<ROOM_MAP>") == "started")
for index, row in ipairs(rows) do
  assert(feedLine(row, "ansi-" .. index) == "row")
end
assert(feedLine("</ROOM_MAP>") == "finished")
assert(feedLine("") == "ignored")
assert(feedLine("description   with spaces") == "ignored")
assert(feedLine("Prompt> ") == "ignored")

assert(#destination == #rows, "room map row count changed")
for index, row in ipairs(rows) do
  assert(destination[index] == " " .. row, "room row changed at " .. index)
  assert(destinationStyles[index] == "ansi-" .. index, "ANSI style was not copied")
end
assert(#main == 4, "map content leaked into the main console")
assert(main[1].text == "before" and main[2].text == "")
assert(main[3].text == "description   with spaces" and main[4].text == "Prompt> ")
assert(#fitCalls == 1 and fitCalls[1].kind == "room")
assert(fitCalls[1].columns == 20 and fitCalls[1].rows == 9)
assert(GUI.AsciiMapCapture.state == nil)
assert(timers["asciiMapCapture.inactivity"] == nil)
"""
        )

    def _test_supported_heights_and_blank_rows(self):
        self._run_lua(
            r"""
for _, height in ipairs({3, 9, 11, 13, 25}) do
  local width = (height * 2) + 1
  assert(feedLine("<ROOM_MAP>") == "started")
  for row = 1, height do
    assert(feedLine(repeatedRow(width, row % 2 == 0 and "|" or ".")) == "row")
  end
  assert(feedLine("</ROOM_MAP>") == "finished")
  assert(#destination == height, "height was truncated: " .. height)
  assert(destination[1] == " " .. repeatedRow(width, "."))
  local finalSymbol = height % 2 == 0 and "|" or "."
  assert(destination[height] == " " .. repeatedRow(width, finalSymbol))
  local fit = fitCalls[#fitCalls]
  assert(fit.kind == "room" and fit.columns == width + 1 and fit.rows == height)
end

assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine("") == "row")
assert(feedLine(".      ") == "row")
assert(feedLine("") == "row")
assert(feedLine("</ROOM_MAP>") == "finished")
assert(#destination == 3)
assert(destination[1] == " " and destination[2] == " .      " and destination[3] == " ")
assert(fitCalls[#fitCalls].rows == 3 and fitCalls[#fitCalls].columns == 8)
"""
        )

    def _test_wilderness_and_multiple_blocks(self):
        self._run_lua(
            r"""
assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine(repeatedRow(19, ".")) == "row")
assert(feedLine("<WILDERNESS_MAP>") == "started", "new opener did not replace capture")
for row = 1, 21 do
  assert(feedLine(repeatedRow(21, row == 11 and "*" or "~")) == "row")
end
assert(feedLine("</WILDERNESS_MAP>") == "finished")
assert(#destination == 21 and destination[1] == "  " .. repeatedRow(21, "~"))
assert(destination[11] == "  " .. repeatedRow(21, "*"))
assert(destination[21] == "  " .. repeatedRow(21, "~"))
assert(clearCount == 2, "each opening marker must clear exactly once")
assert(#fitCalls == 1 and fitCalls[1].kind == "wilderness")
assert(fitCalls[1].columns == 23 and fitCalls[1].rows == 21)
assert(#main == 0, "successful maps leaked into main output")
"""
        )

    def _test_invalid_and_mismatched_recovery(self):
        self._run_lua(
            r"""
assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine(repeatedRow(19, ".")) == "row")
assert(feedLine("This is ordinary prose.") == "aborted")
assert(main[#main].text == "This is ordinary prose.")
assert(feedLine("Prompt> ") == "ignored")
assert(main[#main].text == "Prompt> ")
assert(GUI.AsciiMapCapture.state == nil)

assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine(repeatedRow(19, ".")) == "row")
assert(feedLine("</WILDERNESS_MAP>") == "aborted")
assert(main[#main].text == "</WILDERNESS_MAP>")
assert(feedLine("after mismatch") == "ignored")

assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine(repeatedRow(19, ".")) == "row")
assert(feedLine(repeatedRow(18, ".")) == "aborted")
assert(main[#main].text == repeatedRow(18, "."))

assert(feedLine("<ROOM_MAP>") == "started")
fireTimer("asciiMapCapture.inactivity")
assert(GUI.AsciiMapCapture.state == nil)
assert(feedLine("after timeout") == "ignored")
assert(main[#main].text == "after timeout")
"""
        )

    def _test_destination_failures_preserve_current_line(self):
        self._run_lua(
            r"""
map.minimap = nil
assert(feedLine("<ROOM_MAP>") == "ignored")
assert(main[#main].text == "<ROOM_MAP>", "missing destination consumed opener")

map.minimap = {echo = function(_, value)
  if value:sub(-1) ~= "\n" then pendingPrefix = pendingPrefix .. value end
end}
assert(feedLine("<ROOM_MAP>") == "started")
failAppend = true
assert(feedLine(repeatedRow(19, ".")) == "aborted")
assert(main[#main].text == repeatedRow(19, "."), "append failure consumed row")
assert(GUI.AsciiMapCapture.state == nil)

failAppend = false
failClear = true
assert(feedLine("<ROOM_MAP>") == "ignored")
assert(main[#main].text == "<ROOM_MAP>", "clear failure consumed opener")
"""
        )

    def _test_safety_limit_and_next_map_recovery(self):
        self._run_lua(
            r"""
local row = repeatedRow(19, ".")
assert(feedLine("<ROOM_MAP>") == "started")
for _ = 1, 64 do assert(feedLine(row) == "row") end
assert(feedLine(row) == "aborted")
assert(main[#main].text == row, "oversized row was consumed")
assert(feedLine("ordinary after limit") == "ignored")
assert(main[#main].text == "ordinary after limit")

assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine(row) == "row")
assert(feedLine("</ROOM_MAP>") == "finished")
assert(#destination == 1 and destination[1] == " " .. row)
"""
        )

    def _test_lifecycle_reset_hooks(self):
        sources = {
            "cleanup": self.repo_root
            / "theGUI"
            / "src"
            / "scripts"
            / "gui"
            / "01_preferences.xml",
            "refresh": self.repo_root
            / "theGUI"
            / "src"
            / "scripts"
            / "gui"
            / "52_refresh.xml",
            "connection": self.repo_root
            / "theGUI"
            / "src"
            / "scripts"
            / "gui"
            / "53_lifecycle.xml",
        }
        for boundary, path in sources.items():
            source = path.read_text(encoding="utf-8")
            if "GUI.AsciiMapCapture.reset" not in source:
                raise AssertionError(f"{boundary} does not reset active map capture")

        self._run_lua(
            r"""
assert(feedLine("<ROOM_MAP>") == "started")
assert(feedLine(repeatedRow(19, ".")) == "row")
assert(GUI.AsciiMapCapture.reset("test lifecycle boundary") == true)
assert(GUI.AsciiMapCapture.state == nil)
assert(timers["asciiMapCapture.inactivity"] == nil)
assert(feedLine("ordinary after lifecycle reset") == "ignored")
assert(main[#main].text == "ordinary after lifecycle reset")
"""
        )

    def run_tests(self):
        print("Running output capture regression tests...")
        if not self.lua_path:
            self.errors.append("lua interpreter not found in PATH")
            print("  ✗ Lua is required for output capture regression tests")
            return False

        tests = [
            (
                "permanent_trigger_and_spacing",
                self._test_permanent_trigger_and_spacing_contract,
            ),
            (
                "exact_room_fixture_and_formatting",
                self._test_exact_room_fixture_and_formatting,
            ),
            (
                "supported_heights_and_blank_rows",
                self._test_supported_heights_and_blank_rows,
            ),
            (
                "wilderness_and_multiple_blocks",
                self._test_wilderness_and_multiple_blocks,
            ),
            (
                "invalid_and_mismatched_recovery",
                self._test_invalid_and_mismatched_recovery,
            ),
            (
                "destination_failure_recovery",
                self._test_destination_failures_preserve_current_line,
            ),
            (
                "safety_limit_and_next_map",
                self._test_safety_limit_and_next_map_recovery,
            ),
            ("lifecycle_reset_hooks", self._test_lifecycle_reset_hooks),
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
        print(f"Output capture results: {passed}/{len(tests)} passed")
        return passed == len(tests)

    def get_results(self):
        return {
            "test_results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    tester = OutputCaptureTester()
    success = tester.run_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
