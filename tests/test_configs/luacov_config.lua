local coverageDir = assert(
    os.getenv("LUMINARI_LUA_COVERAGE_DIR"),
    "LUMINARI_LUA_COVERAGE_DIR is required"
)

return {
    statsfile = os.getenv("LUMINARI_LUACOV_STATS_FILE")
        or coverageDir .. "/luacov.raw.stats.out",
    reportfile = os.getenv("LUMINARI_LUACOV_REPORT_FILE")
        or coverageDir .. "/luacov-lines.tsv",
    codefromstrings = false,
    runreport = false,
    deletestats = false,
}
