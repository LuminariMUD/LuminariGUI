local static_dispatch = { look = function() send("look") end }
static_dispatch.look()

GUI.runKnownAction("look")
send("look")

local profile_path = getMudletHomeDir() .. "/LuminariGUI/config.lua"
io.open(profile_path, "w")

tempTimer(1, function()
  send("look")
end)

GUI.Status:echo("Ready")
GUI.debug("PROTOCOL", "subscription complete")
