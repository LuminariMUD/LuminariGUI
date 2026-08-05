---@meta Mudlet 4.22 Geyser

---@class GeyserObject
---@field [string] any
local GeyserObject = {}

---@param constraints? table
---@param parent? GeyserObject
---@return GeyserObject
function GeyserObject:new(constraints, parent) end

---@param stylesheet string
function GeyserObject:setStyleSheet(stylesheet) end

---@param text? any
---@param color? string
---@param format? string
function GeyserObject:echo(text, color, format) end

function GeyserObject:clear() end

function GeyserObject:show() end

function GeyserObject:hide() end

function GeyserObject:raise() end

function GeyserObject:lower() end

---@param x number|string
---@param y number|string
function GeyserObject:move(x, y) end

---@param width number|string
---@param height number|string
function GeyserObject:resize(width, height) end

---@param constraints table
function GeyserObject:set_constraints(constraints) end

---@param size number
function GeyserObject:setFontSize(size) end

---@param color string
function GeyserObject:setColor(color) end

---@param format string
function GeyserObject:setFormat(format) end

---@param callback MudletCallback
---@param ... any
function GeyserObject:setClickCallback(callback, ...) end

---@param callback MudletCallback
---@param ... any
function GeyserObject:setReleaseCallback(callback, ...) end

---@return number
function GeyserObject:get_width() end

---@return number
function GeyserObject:get_height() end

---@class GeyserClass: GeyserObject
local GeyserClass = {}

---@type table<string, GeyserClass>
Geyser = {
  AdjustableContainer = GeyserClass,
  Container = GeyserClass,
  Gauge = GeyserClass,
  HBox = GeyserClass,
  Label = GeyserClass,
  Mapper = GeyserClass,
  MiniConsole = GeyserClass,
  ScrollBox = GeyserClass,
  VBox = GeyserClass,
}

geyser = Geyser

Adjustable = {
  Container = GeyserClass,
}
