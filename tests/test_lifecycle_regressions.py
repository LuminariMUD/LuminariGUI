#!/usr/bin/env python3
"""
Regression tests for Mudlet lifecycle handling and the Python tooling.

The lifecycle cases execute production Lua with small Mudlet mocks. Tooling
cases use isolated project copies (and a temporary Git repository for release)
so versioning, packaging, and drift checks are exercised without mutating the
working tree.
"""

import html
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path


class LifecycleRegressionTester:
    def __init__(self, _xml_file=None):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.mapper_source_path = (
            self.repo_root / "theGUI" / "src" / "scripts" / "00_msdpmapper.xml"
        )
        self.debug_source_path = (
            self.repo_root / "theGUI" / "src" / "scripts" / "00_debug.xml"
        )
        self.adjustable_source_path = (
            self.repo_root
            / "theGUI"
            / "src"
            / "scripts"
            / "00_adjustablecontainers.xml"
        )
        self.instrumentation_source_path = (
            self.repo_root
            / "theGUI"
            / "src"
            / "scripts"
            / "99_debug_instrumentation.xml"
        )
        self.lua_path = self._find_lua()
        self.test_results = []
        self.errors = []
        self.warnings = []
        self._gui_scripts_cache = None
        self._gui_script_order_cache = None

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

    def _load_gui_scripts(self):
        """Assemble current sources and index inner-GUI Lua by Mudlet name."""
        if self._gui_scripts_cache is not None:
            return self._gui_scripts_cache

        module_path = self.repo_root / "theGUI" / "build.py"
        spec = importlib.util.spec_from_file_location(
            "luminari_gui_source_probe",
            module_path,
        )
        if spec is None or spec.loader is None:
            raise AssertionError("could not load build.py for GUI source assembly")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        build_log = io.StringIO()
        with redirect_stdout(build_log):
            success, assembled = module.Builder(module.BuildConfig()).build(
                validate_only=True
            )
        self._require(
            success,
            "could not assemble current GUI sources:\n" + build_log.getvalue(),
        )
        self._require(
            "BUILD_INCLUDE:" not in assembled,
            "build include directive leaked into assembled XML",
        )

        root = ET.fromstring(assembled)
        script_package = root.find("ScriptPackage")
        self._require(script_package is not None, "assembled XML has no ScriptPackage")
        outer_gui = next(
            (
                node
                for node in script_package.iter("ScriptGroup")
                if node.findtext("name") == "GUI"
            ),
            None,
        )
        self._require(outer_gui is not None, "assembled XML has no outer GUI group")
        inner_gui = next(
            (
                node
                for node in outer_gui.findall("./ScriptGroup")
                if node.findtext("name") == "GUI"
            ),
            None,
        )
        self._require(inner_gui is not None, "assembled XML has no inner GUI group")

        scripts = {}
        order = []
        for node in inner_gui.findall("./Script"):
            name = node.findtext("name")
            self._require(name, "inner GUI contains an unnamed Script")
            self._require(name not in scripts, f"duplicate inner GUI script name: {name}")
            scripts[name] = node.findtext("script") or ""
            order.append(name)

        self._gui_scripts_cache = scripts
        self._gui_script_order_cache = order
        return scripts

    def _gui_script(self, name):
        scripts = self._load_gui_scripts()
        self._require(name in scripts, f"assembled GUI script was not found: {name}")
        return scripts[name]

    def _gui_lua_source(self):
        scripts = self._load_gui_scripts()
        return "\n".join(scripts[name] for name in self._gui_script_order_cache)

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
        source = self._gui_script("GUI Event Registry")
        register_function = source[source.index("function GUI.registerEventHandlers()"):]

        script = f'''
GUI = {{
  DEBUG = false,
  debug = function() end,
  debugError = function() end,
  debugCountEntries = function() return 0 end,
  debugWrap = function(_, callable) return callable end,
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

    def _test_mapper_initializer_is_idempotent(self):
        source = self.mapper_source_path.read_text(encoding="utf-8")
        initializer = self._extract(
            source,
            "local function mapperRuntimeReady()",
            "\nfunction map.get_default_map()",
        )

        script = f'''
local createCalls = 0
local aliasCalls = 0
local fontCalls = 0
local mapDownloadChecks = 0

local function fakeWindow(name, parent)
  local window = {{name = name, container = parent}}
  function window:setColor() end
  function window:hide() end
  function window:show() end
  function window:resize() end
  return window
end

GUI = {{
  debug = function() end,
  debugCountEntries = function() return 0 end,
  debugWrap = function(_, callable) return callable end,
  AdjustableContainers = {{
    defaultStyle = {{}},
    saveDir = "/tmp/luminari-layouts/",
    create = function(name)
      createCalls = createCalls + 1
      return fakeWindow(name)
    end,
  }},
}}

Geyser = {{MiniConsole = {{}}, Mapper = {{}}}}
function Geyser.MiniConsole:new(config, parent)
  return fakeWindow(config.name, parent)
end
function Geyser.Mapper:new(config, parent)
  return fakeWindow(config.name, parent)
end

map = {{
  adjustMinimapFontSize = function()
    fontCalls = fontCalls + 1
  end,
  get_default_map = function()
    mapDownloadChecks = mapDownloadChecks + 1
  end,
}}
defaults = {{mapper = {{x = "75%", y = "0%", width = "25%", height = "50%"}}}}
terrain_types = {{}}

local function make_aliases()
  aliasCalls = aliasCalls + 1
end

function setCustomEnvColor() end
function tempTimer(_, callback) callback() end

{initializer}

assert(map.initialize() == true)
local firstMapContainer = map.container
local firstAsciiContainer = GUI.asciiMapContainer
local firstMapWindow = map.mapwindow
local firstMinimap = map.minimap

assert(map.initialize() == true)
assert(createCalls == 2, "second mapper initialization recreated containers")
assert(aliasCalls == 1, "second mapper initialization recreated aliases")
assert(fontCalls == 1, "second mapper initialization resized the ASCII map")
assert(mapDownloadChecks == 1, "second mapper initialization repeated map setup")
assert(map.container == firstMapContainer)
assert(GUI.asciiMapContainer == firstAsciiContainer)
assert(map.mapwindow == firstMapWindow)
assert(map.minimap == firstMinimap)
'''
        self._run_lua(script)

    def _test_profile_reset_initializes_mapper(self):
        source = self._gui_script("GUI Lifecycle")
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
  debug = function() end,
  debugCall = function(_, callable, ...)
    return true, callable(...)
  end,
  debugWrap = function(_, callable)
    return callable
  end,
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

    def _test_debug_master_toggle_and_load_order(self):
        debug_source = self.debug_source_path.read_text(encoding="utf-8")
        instrumentation_source = self.instrumentation_source_path.read_text(
            encoding="utf-8"
        )
        manifest = (self.repo_root / "theGUI" / "build.yaml").read_text(
            encoding="utf-8"
        )

        script_block = manifest.split("scripts:", 1)[1].split("keys:", 1)[0]
        scripts = re.findall(r"-\s+(src/scripts/[^\s]+)", script_block)
        self._require(scripts, "build manifest has no script fragments")
        self._require(
            scripts[0] == "src/scripts/00_debug.xml",
            "debug bootstrap is not the first script fragment",
        )
        self._require(
            scripts[-1] == "src/scripts/99_debug_instrumentation.xml",
            "debug instrumentation is not the last script fragment",
        )
        self._require(
            scripts.index("src/scripts/00_adjustablecontainers.xml")
            < scripts.index("src/scripts/01_gui.xml"),
            "AdjustableContainers foundation does not load before the GUI wrapper",
        )
        self._require(
            scripts.index("src/scripts/00_msdpmapper.xml")
            < scripts.index("src/scripts/01_gui.xml")
            < scripts.index("src/scripts/02_yatcoconfig.xml"),
            "composite GUI entry is not between the mapper and YATCOConfig",
        )

        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (self.repo_root / "theGUI" / "src").rglob("*.xml")
        )
        explicit_boolean_assignments = re.findall(
            r"\bGUI\.DEBUG\s*=\s*(?:true|false)\b", source_text
        )
        self._require(
            explicit_boolean_assignments == ["GUI.DEBUG = false"],
            "GUI.DEBUG must have exactly one explicit boolean assignment set to false",
        )
        self._require(
            "This is the ONE switch" in debug_source,
            "master debug toggle is not documented as the single switch",
        )
        self._require(
            "demonnic.debug.active = (GUI.DEBUG == true)" in source_text,
            "legacy YATCO debug state does not mirror the master switch",
        )
        self._require(
            "wrapTableFunctions(GUI.AdjustableContainers" in instrumentation_source,
            "adjustable containers are not instrumented",
        )
        self._require(
            "mapWindow = type(map and map.mapwindow)" in instrumentation_source,
            "debug snapshot checks the wrong Mudlet mapper field",
        )
        self._require(
            "asciiMapWindow = type(map and map.minimap)" in instrumentation_source,
            "debug snapshot checks the wrong ASCII mapper field",
        )

    def _test_gui_script_names_and_order(self):
        self._load_gui_scripts()
        expected = [
            "Toggles",
            "Create Background",
            "Set Borders",
            "Boxes",
            "Gauges",
            "Cast Console",
            "Header Icons",
            "TabbedInfoWindow",
            "Affects",
            "Group",
            "Player",
            "Buttons",
            "Room Info/Legend",
            "DrawFrames",
            "MSDP Protocol",
            "MSDP Gauges",
            "MSDP Actions",
            "GUI Boot",
            "GUI Event Registry",
            "GUI Refresh",
            "GUI Lifecycle",
            "AdjustableContainers",
            "Custom Scrollbar",
            "Delete Line and  Prompt",
        ]
        self._require(
            self._gui_script_order_cache == expected,
            "unexpected inner GUI script order: "
            + " -> ".join(self._gui_script_order_cache),
        )

    def _test_gui_wrapper_and_fragment_sizes(self):
        wrapper_path = (
            self.repo_root / "theGUI" / "src" / "scripts" / "01_gui.xml"
        )
        wrapper = wrapper_path.read_text(encoding="utf-8")
        wrapper_lines = len(wrapper.splitlines())
        self._require(
            wrapper_lines < 100,
            f"composite GUI wrapper is too large: {wrapper_lines} lines",
        )

        include_paths = re.findall(
            r"<!--\s*BUILD_INCLUDE:\s*(gui/[^\s]+)\s*-->",
            wrapper,
        )
        self._require(include_paths, "GUI wrapper has no child includes")
        self._require(
            len(include_paths) == len(set(include_paths)),
            "GUI wrapper includes the same child more than once",
        )

        for rel_path in include_paths:
            path = wrapper_path.parent / rel_path
            self._require(path.is_file(), f"GUI child does not exist: {rel_path}")
            root = ET.fromstring(
                "<root>" + path.read_text(encoding="utf-8") + "</root>"
            )
            scripts = root.findall(".//Script")
            for script_node in scripts:
                name = script_node.findtext("name") or rel_path
                lua_lines = len((script_node.findtext("script") or "").splitlines())
                self._require(
                    lua_lines <= 300,
                    f"GUI child {name} exceeds 300 Lua lines: {lua_lines}",
                )

    def _test_core_parent_load_order_and_orphan_guard(self):
        foundation_root = ET.parse(self.adjustable_source_path).getroot()
        foundation_script = foundation_root.find(".//Script/script").text
        self._require(
            foundation_script,
            "AdjustableContainers foundation has no Lua script",
        )

        buttons_script = self._gui_script("Buttons")
        boxes_script = self._gui_script("Boxes")
        gui_source = self._gui_lua_source()
        self._require(
            "function GUI.AdjustableContainers.create" not in gui_source,
            "AdjustableContainers foundation is duplicated inside late GUI scripts",
        )
        button_init = gui_source.index("function GUI.buttonWindow.init()")
        parent_guard = gui_source.index(
            'type(GUI.buttonPanelContainer) ~= "table"',
            button_init,
        )
        first_widget_creation = gui_source.index("CSSMan.new(", button_init)
        self._require(
            parent_guard < first_widget_creation,
            "button parent guard runs after widget creation",
        )

        script = f'''
GUI = {{debug = function() end}}
function getMudletHomeDir()
  return "/tmp/luminari-test-profile"
end

{foundation_script}

assert(type(GUI.AdjustableContainers) == "table")
assert(type(GUI.AdjustableContainers.create) == "function")

map = {{}}
{buttons_script}

local ok, failure = pcall(GUI.buttonWindow.init)
assert(ok == false, "button initialization accepted missing parents")
assert(
  tostring(failure):find("refusing to create root-level controls", 1, true),
  "button initialization failed without the orphan-control explanation"
)
'''
        self._run_lua(script)

        healthy_bootstrap = f'''
local rootWidgets = {{}}

local function newWindow(config, parent)
  if parent == nil then
    rootWidgets[#rootWidgets + 1] = config.name
  end
  local window = {{
    name = config.name,
    container = parent,
    windowList = {{}},
  }}
  function window:setStyleSheet() end
  function window:setClickCallback() end
  function window:setColor() end
  function window:echo() end
  function window:show() end
  function window:hide() end
  function window:raise() end
  function window:get_width() return 250 end
  function window:get_height() return 150 end
  function window:delete() self.deleted = true end
  return window
end

GUI = {{debug = function() end}}
function getMudletHomeDir()
  return "/tmp/luminari-test-profile"
end

Adjustable = {{Container = {{all = {{}}}}}}
function Adjustable.Container:new(config)
  local window = newWindow(config, {{name = "GeyserRoot"}})
  function window:disableAutoSave() end
  function window:detach() end
  Adjustable.Container.all[config.name] = window
  return window
end

Geyser = {{Label = {{}}, Container = {{}}, HBox = {{}}, MiniConsole = {{}}}}
function Geyser.Label:new(config, parent)
  return newWindow(config, parent)
end
function Geyser.Container:new(config, parent)
  return newWindow(config, parent)
end
function Geyser.HBox:new(config, parent)
  return newWindow(config, parent)
end
function Geyser.MiniConsole:new(config, parent)
  return newWindow(config, parent)
end

CSSMan = {{}}
function CSSMan.new()
  return {{
    getCSS = function() return "" end,
    set = function() end,
  }}
end

function calcFontSize(fontSize)
  return fontSize, fontSize
end
function setMiniConsoleFontSize() end

{foundation_script}

GUI.Bottom = newWindow({{name = "GUI.Bottom"}}, {{name = "GeyserRoot"}})
GUI.Right = newWindow({{name = "GUI.Right"}}, {{name = "GeyserRoot"}})

{boxes_script}
GUI.init_boxes()

assert(type(GUI.buttonPanelContainer) == "table")
assert(type(GUI.roomInfoContainer) == "table")

map = {{}}
GUI.updateLegend = function() end
{buttons_script}
GUI.buttonWindow.init()

assert(
  #rootWidgets == 0,
  "core GUI bootstrap created root-level child widgets: "
    .. table.concat(rootWidgets, ", ")
)
assert(GUI.buttonWindow.container.container == GUI.buttonPanelContainer)
assert(GUI.buttonWindow.roomInfo.container == GUI.roomInfoContainer)
assert(GUI.buttonWindow.Legend.container == GUI.roomInfoContainer)
'''
        self._run_lua(healthy_bootstrap)

    def _test_debug_runtime_output_and_error_semantics(self):
        root = ET.parse(self.debug_source_path).getroot()
        debug_script = root.find(".//Script/script").text
        self._require(debug_script, "debug bootstrap has no Lua script")

        script = f'''
captured = {{}}
function echo(value)
  captured[#captured + 1] = value
end
function cecho(value)
  captured[#captured + 1] = value
end

{debug_script}

assert(GUI.DEBUG == false, "debug mode is not disabled by default")
GUI.DEBUG = true
GUI.debug("TEST", "visible message", {{answer = 42}})
local joined = table.concat(captured, "\\n")
assert(joined:find("LGUI%-DEBUG"), "debug prefix was not written")
assert(joined:find("visible message", 1, true), "debug message was not written")
assert(joined:find("answer=42", 1, true), "debug details were not written")

local ok, failure = GUI.debugCall("TEST/failure", function()
  error("intentional debug failure")
end)
assert(ok == false, "debug mode did not catch the test error")
assert(tostring(failure):find("intentional debug failure", 1, true))
joined = table.concat(captured, "\\n")
assert(joined:find("LGUI%-ERROR"), "error prefix was not written")
assert(joined:find("LGUI%-TRACE"), "stack trace lines were not written")
assert(joined:find("intentional debug failure", 1, true))

local wrapped = GUI.debugWrap("TEST/multiple returns", function()
  return "first", nil, "third"
end)
local first, second, third = wrapped()
assert(first == "first" and second == nil and third == "third",
  "debug wrapper changed multiple return values")

local beforeDisabledCall = #captured
GUI.DEBUG = false
GUI.debug("TEST", "must stay hidden")
assert(#captured == beforeDisabledCall, "debug output continued while disabled")
local propagated = pcall(function()
  GUI.debugCall("TEST/disabled failure", function()
    error("must propagate")
  end)
end)
assert(propagated == false,
  "disabled debug mode swallowed an error instead of preserving production behavior")
'''
        self._run_lua(script)

    def _test_debug_startup_boundary_and_system_coverage(self):
        gui_source = self._gui_lua_source()
        boot_source = self._gui_script("GUI Boot")
        refresh_source = self._gui_script("GUI Refresh")
        mapper_source = self.mapper_source_path.read_text(encoding="utf-8")
        yatco_source = (
            self.repo_root / "theGUI" / "src" / "scripts" / "03_yatco.xml"
        ).read_text(encoding="utf-8")
        trigger_source = (
            self.repo_root / "theGUI" / "src" / "triggers" / "01_gui.xml"
        ).read_text(encoding="utf-8")
        alias_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (self.repo_root / "theGUI" / "src" / "aliases").glob("*.xml")
        )
        key_path = self.repo_root / "theGUI" / "src" / "keys" / "00_movement.xml"

        initializer = gui_source.index("function GUI.initializeOrRefresh(context)")
        for stage in (
            "GUI.init_background",
            "GUI.set_borders",
            "GUI.init_boxes",
        ):
            stage_position = gui_source.index(
                f'{{name = "{stage}", callable = {stage}}}'
            )
            self._require(
                stage_position < initializer,
                f"{stage} is not guarded before initializeOrRefresh is defined",
            )
        self._require(
            '"BOOT/CONFIG/" .. stage.name' in boot_source,
            "startup stages do not run through the debug error boundary",
        )
        self._require(
            "function GUI.initializeOrRefresh(context)" in refresh_source,
            "GUI Refresh does not define initializeOrRefresh",
        )

        coverage_markers = {
            "GUI initialization": (gui_source, "GUI/INIT"),
            "GUI lifecycle": (gui_source, "LIFECYCLE"),
            "event registration": (gui_source, "EVENT/REGISTER"),
            "event firing": (gui_source, "EVENT/FIRE"),
            "MSDP reports": (gui_source, "MSDP/REPORT"),
            "MSDP values": (gui_source, "MSDP/VALUE"),
            "mapper events": (mapper_source, "MAPPER/EVENT"),
            "mapper initialization": (mapper_source, "MAPPER/INIT"),
            "map triggers": (trigger_source, "TRIGGER/MAP"),
            "chat creation": (yatco_source, "YATCO/CREATE"),
            "chat capture": (yatco_source, "YATCO/APPEND"),
            "aliases": (alias_source, 'GUI.debug("ALIAS"'),
        }
        for area, (source, marker) in coverage_markers.items():
            self._require(marker in source, f"missing debug coverage for {area}")

        key_root = ET.fromstring(
            "<root>" + key_path.read_text(encoding="utf-8") + "</root>"
        )
        keys = key_root.findall(".//Key")
        self._require(keys, "movement key fragment has no keys")
        for key in keys:
            name = key.findtext("name")
            script = key.findtext("script") or ""
            self._require(
                'GUI.debug("KEY"' in script,
                f"key {name} does not emit debug details",
            )

    def _test_debug_event_callbacks_keep_their_event_and_handler(self):
        source = self._gui_script("GUI Event Registry")
        register_function = source[source.index("function GUI.registerEventHandlers()"):]

        script = f'''
handlers = {{}}
next_id = 0
calls = {{health = 0, room = 0}}
msdp = {{HEALTH = 17, ROOM = {{VNUM = 99}}}}
demonnic = {{chat = {{use = false}}}}

local resolved = {{
  ["GUI.updateHealthGauge"] = function(event)
    assert(event == "msdp.HEALTH")
    calls.health = calls.health + 1
  end,
  ["GUI.updateRoom"] = function(event)
    assert(event == "msdp.ROOM")
    calls.room = calls.room + 1
  end,
}}

GUI = {{
  DEBUG = true,
  eventHandlerIds = {{}},
  debug = function() end,
  debugError = function(_, message) error(message) end,
  debugCountEntries = function() return 0 end,
  debugResolve = function(path)
    return resolved[path] or function() end
  end,
  debugCall = function(_, callable, ...)
    return true, callable(...)
  end,
  debugWrap = function(_, callable)
    return callable
  end,
}}

function registerAnonymousEventHandler(event, callback)
  next_id = next_id + 1
  handlers[event] = callback
  return next_id
end
function killAnonymousEventHandler() return true end
function tempTimer() end

{register_function}

GUI.registerEventHandlers()
assert(type(handlers["msdp.HEALTH"]) == "function")
assert(type(handlers["msdp.ROOM"]) == "function")
handlers["msdp.HEALTH"]("msdp.HEALTH")
handlers["msdp.ROOM"]("msdp.ROOM")
assert(calls.health == 1, "HEALTH callback lost its loop-local handler")
assert(calls.room == 1, "ROOM callback lost its loop-local handler")
'''
        self._run_lua(script)

    def _copy_build_tree(self, destination):
        project_root = destination / "project"
        shutil.copytree(self.repo_root / "theGUI", project_root / "theGUI")
        return project_root

    @staticmethod
    def _configure_composite_fixture(
        project_root,
        wrapper_include="parts/child.xml",
        child_include="grandchild.xml",
        grandchild_content=None,
    ):
        fixture_dir = (
            project_root / "theGUI" / "src" / "scripts" / "include_test"
        )
        parts_dir = fixture_dir / "parts"
        parts_dir.mkdir(parents=True, exist_ok=True)

        wrapper_path = fixture_dir / "wrapper.xml"
        child_path = parts_dir / "child.xml"
        grandchild_path = parts_dir / "grandchild.xml"
        wrapper_path.write_text(
            """<ScriptGroup isActive="yes" isFolder="yes">
\t<name>Include Test</name>
\t<packageName></packageName>
\t<script></script>
\t<eventHandlerList />
\t<!-- BUILD_INCLUDE: """
            + wrapper_include
            + """ -->
</ScriptGroup>
""",
            encoding="utf-8",
        )
        child_path.write_text(
            "<!-- BUILD_INCLUDE: " + child_include + " -->\n",
            encoding="utf-8",
        )
        if grandchild_content is None:
            grandchild_content = """<Script isActive="yes" isFolder="no">
\t<name>Included Grandchild</name>
\t<packageName></packageName>
\t<script>includedProbe = true</script>
\t<eventHandlerList />
</Script>
"""
        grandchild_path.write_text(grandchild_content, encoding="utf-8")

        config_path = project_root / "theGUI" / "build.yaml"
        config = config_path.read_text(encoding="utf-8")
        config = config.replace(
            "  - src/scripts/01_gui.xml\n",
            "  - src/scripts/include_test/wrapper.xml\n",
        )
        config_path.write_text(config, encoding="utf-8")
        return wrapper_path, child_path, grandchild_path

    @staticmethod
    def _load_build_module(project_root):
        module_path = project_root / "theGUI" / "build.py"
        module_name = f"luminari_build_include_probe_{id(project_root)}"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise AssertionError("could not load build.py for include probe")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _test_composite_includes_build_stats_fallback_and_watch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            _, _, grandchild_path = self._configure_composite_fixture(project_root)
            version = self._manifest_version(project_root)

            build = self._run_build_check(
                project_root,
                "--version",
                version,
            )
            self._require(build.returncode == 0, build.stdout + build.stderr)
            output = (project_root / "LuminariGUI.xml").read_text(encoding="utf-8")
            self._require(
                "<name>Included Grandchild</name>" in output,
                "nested relative include was not expanded",
            )
            self._require(
                "BUILD_INCLUDE:" not in output,
                "build include directive leaked into assembled XML",
            )

            stats = self._run_build_check(project_root, "--stats")
            self._require(stats.returncode == 0, stats.stdout + stats.stderr)
            self._require(
                "include src/scripts/include_test/parts/child.xml" in stats.stdout,
                "stats did not report the included child separately",
            )
            self._require(
                "include src/scripts/include_test/parts/grandchild.xml"
                in stats.stdout,
                "stats did not report the nested include separately",
            )

            fallback = subprocess.run(
                [
                    sys.executable,
                    "-S",
                    str(project_root / "theGUI" / "build.py"),
                    "--validate",
                ],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self._require(
                fallback.returncode == 0,
                "include expansion failed without PyYAML:\n"
                + fallback.stdout
                + fallback.stderr,
            )

            build_module = self._load_build_module(project_root)
            config = build_module.BuildConfig(
                project_root / "theGUI" / "build.yaml"
            )
            watcher = build_module.Watcher(build_module.Builder(config))
            baseline = watcher.latest_mtime()
            os.utime(grandchild_path, (baseline + 5, baseline + 5))
            self._require(
                watcher.latest_mtime() > baseline,
                "watch mode did not discover a nested included XML change",
            )

    def _test_composite_include_diagnostics(self):
        cases = (
            (
                {"wrapper_include": "parts/missing.xml"},
                "Included fragment not found",
            ),
            (
                {"wrapper_include": "../../../skeleton.xml"},
                "escapes the source tree",
            ),
            (
                {"wrapper_include": "parts/*.xml"},
                "cannot use globs",
            ),
            (
                {"grandchild_content": "<Script>\n"},
                "Invalid source fragment",
            ),
            (
                {"child_include": "../wrapper.xml"},
                "include cycle detected",
            ),
        )

        for fixture_options, expected_message in cases:
            with tempfile.TemporaryDirectory() as temp_dir:
                project_root = self._copy_build_tree(Path(temp_dir))
                self._configure_composite_fixture(project_root, **fixture_options)
                result = self._run_build_check(project_root, "--validate")
                combined = result.stdout + result.stderr
                self._require(
                    result.returncode != 0,
                    f"invalid include unexpectedly passed: {fixture_options}",
                )
                self._require(
                    expected_message in combined,
                    f"missing diagnostic {expected_message!r}: {combined}",
                )

    def _test_extract_refuses_composite_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = self._copy_build_tree(Path(temp_dir))
            wrapper_path, child_path, _ = self._configure_composite_fixture(
                project_root
            )
            shutil.copy2(
                self.repo_root / "LuminariGUI.xml",
                project_root / "LuminariGUI.xml",
            )
            config_path = project_root / "theGUI" / "build.yaml"
            before = {
                path: path.read_bytes()
                for path in (config_path, wrapper_path, child_path)
            }

            result = self._run_build_check(project_root, "--extract")
            combined = result.stdout + result.stderr
            self._require(result.returncode != 0, combined)
            self._require(
                "refuses to overwrite composite source fragments" in combined,
                "--extract did not explain the composite-layout refusal",
            )
            for path, content in before.items():
                self._require(
                    path.read_bytes() == content,
                    f"--extract modified {path.name} before refusing",
                )

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
                "debug_master_toggle_and_load_order",
                self._test_debug_master_toggle_and_load_order,
            ),
            (
                "debug_runtime_output_and_errors",
                self._test_debug_runtime_output_and_error_semantics,
            ),
            (
                "gui_script_names_and_order",
                self._test_gui_script_names_and_order,
            ),
            (
                "gui_wrapper_and_fragment_sizes",
                self._test_gui_wrapper_and_fragment_sizes,
            ),
            (
                "core_parent_load_order_and_orphan_guard",
                self._test_core_parent_load_order_and_orphan_guard,
            ),
            (
                "debug_startup_boundary_and_coverage",
                self._test_debug_startup_boundary_and_system_coverage,
            ),
            (
                "debug_event_callback_mapping",
                self._test_debug_event_callbacks_keep_their_event_and_handler,
            ),
            (
                "upgrade_handler_ownership",
                self._test_upgrade_preserves_file_scope_handler_ids,
            ),
            ("mapper_initializer_exported", self._test_mapper_initializer_is_exported),
            ("mapper_initializer_idempotent", self._test_mapper_initializer_is_idempotent),
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
                "composite_include_build_stats_fallback_watch",
                self._test_composite_includes_build_stats_fallback_and_watch,
            ),
            (
                "composite_include_diagnostics",
                self._test_composite_include_diagnostics,
            ),
            (
                "extract_refuses_composite_sources",
                self._test_extract_refuses_composite_sources,
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
