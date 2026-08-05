local luacovReporter = require("luacov.reporter")

local LuminariReporter = setmetatable({}, luacovReporter.ReporterBase)
LuminariReporter.__index = LuminariReporter

function LuminariReporter:on_start()
    self:write("LUMINARI_LUACOV\t1\n")
end

function LuminariReporter:on_new_file(filename)
    assert(not filename:find("[\t\r\n]"), "unsupported control character in path")
    self:write("F\t", filename, "\n")
end

function LuminariReporter:on_file_error(filename, errorType, message) -- luacheck: no self
    error(string.format("Could not %s %s: %s", errorType, filename, message))
end

function LuminariReporter:on_empty_line(_, lineNumber)
    self:write("L\t", lineNumber, "\texcluded\t0\n")
end

function LuminariReporter:on_mis_line(_, lineNumber)
    self:write("L\t", lineNumber, "\tmissed\t0\n")
end

function LuminariReporter:on_hit_line(_, lineNumber, _, hits)
    self:write("L\t", lineNumber, "\thit\t", hits, "\n")
end

function LuminariReporter:on_end_file(_, hits, missed)
    self:write("S\t", hits, "\t", missed, "\n")
end

local reporter = {}

function reporter.report()
    return luacovReporter.report(LuminariReporter)
end

return reporter
