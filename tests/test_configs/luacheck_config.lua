-- Luacheck configuration for LuminariGUI testing
std = "luajit"

-- Global variables and functions specific to Mudlet and LuminariGUI
globals = {
    -- Mudlet core functions
    "cecho", "decho", "echo", "hecho", "send", "sendAll", "sendRaw",
    "raiseEvent", "registerAnonymousEventHandler", "killAnonymousEventHandler",
    "tempTimer", "killTimer", "tempTrigger", "killTrigger", "tempAlias", "killAlias",
    "tempLineTrigger",
    "getMudletHomeDir", "getProfileName", 
    "pcall", "xpcall", "pairs", "ipairs", "next", "print", "type", "tostring", "tonumber",
    "table", "string", "math", "os", "io", "debug", "coroutine", "package", "require",
    
    -- Mudlet display and window functions
    "display", "clearWindow", "appendBuffer", "deleteLineP", "deleteLine",
    "clearUserWindow", "selectCurrentLine", "copy", "exists",
    "setFont", "getFont", "setMiniConsoleFontSize", "getFontSize", "getColumnCount",
    "setAppStyleSheet", "setBgColor", "getMainWindowSize",
    "getFgColor", "getBgColor", "getTime",
    "setBorderLeft", "setBorderTop", "setBorderBottom", "setBorderRight",
    
    -- Mudlet variables
    "line", "matches", "color_table",
    
    -- MSDP/GMCP data
    "msdp", "gmcp", "atcp", "channel102", "mud",
    "sendMSDP",
    
    -- Mudlet mapping
    "getRoomExits", "getRoomName", "getRoomArea", "getRoomCoordinates",
    "getRoomsByPosition", "getExitStubs1", "getAreaTable", "getAreaRooms",
    "createRoomID", "setRoomCoordinates", "addRoom", "setRoomArea", "addAreaName",
    "setRoomEnv", "setExit", "setExitStub",
    "speedWalk", "getPath", "updateMap", "centerview", "loadMap",
    "setCustomEnvColor",
    
    -- Mudlet networking
    "downloadFile",
    
    -- UI framework
    "Geyser", "geyser",
    
    -- LuminariGUI specific globals
    "GUI", "LUM", "map", "demonnic", "areas", "stubmap", 
    "speedwalk_timer", "speedwalk_vnums", "speedWalkPath", "speedwalk_index",
    "maplineTrig", "roommaplineTrig", "CSSMan",
    
    -- LuminariGUI runtime globals
    "mudlet", -- Mudlet table
    "speedwalk_active", "speedWalkDir", "doSpeedWalk", "downloading",
    "padding", "onMapLine", "onRoomMapLine",
    "affect_string", "affected_by", "num_grouped", "hp_color",
    "createFrame", "ft", "terrain_types",
    "demonnicChatSwitch", "demonnicOnStart", "demonnicOnInstall",
    "calcFontSize"
}

-- Ignore common patterns that are acceptable in Mudlet scripting
ignore = {
    "212", -- Unused argument (common in event handlers)
    "213", -- Unused loop variable
    "311", -- Value assigned to variable is unused (common in Mudlet)
    "411", -- Redefining local variable
    "412", -- Redefining argument
    "421", -- Shadowing local variable
    "422", -- Shadowing argument
    "542", -- Empty if branch
    "611", -- Line contains only whitespace
    "612", -- Line contains trailing whitespace
    "613", -- Trailing whitespace in string
    "614", -- Trailing whitespace in comment
    "621", -- Inconsistent indentation
    "631", -- Line is too long
}

-- File-specific configurations
files = {
    ["tests/sample_scripts/*.lua"] = {
        ignore = {"111", "112", "113"} -- Allow undefined variables in test scripts
    }
}

-- Maximum line length
max_line_length = 120