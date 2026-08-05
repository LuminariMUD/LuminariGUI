---@meta Mudlet 4.22

---@alias MudletCallback string|fun(...: any)

---@param text any
function cecho(text) end

---@param text any
function decho(text) end

---@param text any
function echo(text) end

---@param text any
function hecho(text) end

---@param command string
---@param echo_command? boolean
function send(command, echo_command) end

---@param ... string
function sendAll(...) end

---@param data string
function sendRaw(data) end

---@param event string
---@param ... any
function raiseEvent(event, ...) end

---@param event string
---@param callback MudletCallback
---@param one_shot? boolean
---@return integer handler_id
function registerAnonymousEventHandler(event, callback, one_shot) end

---@param handler_id integer
---@return boolean
function killAnonymousEventHandler(handler_id) end

---@param delay number
---@param callback MudletCallback
---@return integer timer_id
function tempTimer(delay, callback) end

---@param timer_id integer|string
---@return boolean
function killTimer(timer_id) end

---@param pattern string
---@param callback MudletCallback
---@return integer trigger_id
function tempTrigger(pattern, callback) end

---@param trigger_id integer|string
---@return boolean
function killTrigger(trigger_id) end

---@param pattern string
---@param callback MudletCallback
---@return integer alias_id
function tempAlias(pattern, callback) end

---@param alias_id integer|string
---@return boolean
function killAlias(alias_id) end

---@param from integer
---@param how_many integer
---@param callback MudletCallback
---@return integer trigger_id
function tempLineTrigger(from, how_many, callback) end

---@param command string
---@param payload any
function sendMSDP(command, payload) end

---@return string
function getMudletHomeDir() end

---@return string
function getProfileName() end

---@return integer width
---@return integer height
function getMainWindowSize() end

---@param destination string
---@param url string
function downloadFile(destination, url) end

---@param path string
---@return boolean
function loadMap(path) end

---@param room_id integer
function centerview(room_id) end

function updateMap() end

---@param room_id integer
---@return table<string, integer>
function getRoomExits(room_id) end

---@param room_id integer
---@return string
function getRoomName(room_id) end

---@param room_id integer
---@return integer
function getRoomArea(room_id) end

---@param room_id integer
---@return integer x
---@return integer y
---@return integer z
function getRoomCoordinates(room_id) end

---@param x integer
---@param y integer
---@param z integer
---@param area_id integer
---@return integer[]
function getRoomsByPosition(x, y, z, area_id) end

---@return table<string, integer>
function getAreaTable() end

---@param area_id integer
---@return integer[]
function getAreaRooms(area_id) end

---@return integer
function createRoomID() end

---@param room_id integer
---@param x integer
---@param y integer
---@param z integer
function setRoomCoordinates(room_id, x, y, z) end

---@param room_id integer
function addRoom(room_id) end

---@param room_id integer
---@param area_id integer
function setRoomArea(room_id, area_id) end

---@param name string
---@return integer
function addAreaName(name) end

---@param room_id integer
---@param environment integer
function setRoomEnv(room_id, environment) end

---@param from_room integer
---@param to_room integer
---@param direction string
function setExit(from_room, to_room, direction) end

---@param room_id integer
---@param direction string
---@param enabled boolean
function setExitStub(room_id, direction, enabled) end

---@param environment integer
---@param red integer
---@param green integer
---@param blue integer
function setCustomEnvColor(environment, red, green, blue) end

---@param destination integer|string
---@return boolean
function getPath(destination) end

function speedWalk() end

function deleteLine() end

function selectCurrentLine() end

---@return string
function copy() end

---@param name string
---@param kind? string
---@return integer
function exists(name, kind) end

---@param left integer
function setBorderLeft(left) end

---@param top integer
function setBorderTop(top) end

---@param right integer
function setBorderRight(right) end

---@param bottom integer
function setBorderBottom(bottom) end

---@param path string
---@param value table
function table.save(path, value) end

---@param path string
---@param value table
function table.load(path, value) end

---@param value string
---@return string
function string.trim(value) end

---@param value string
---@return string
function string.title(value) end

---@type table<string, any>
msdp = msdp or {}

---@type table<string, any>
gmcp = gmcp or {}

---@type any[]
matches = matches or {}

---@type string
line = line or ""
