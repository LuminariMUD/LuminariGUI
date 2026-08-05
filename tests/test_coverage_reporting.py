#!/usr/bin/env python3
"""Regression tests for source-mapped Lua and split coverage reporting."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XML_FILE = str(PROJECT_ROOT / "LuminariGUI.xml")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lua_coverage import (  # noqa: E402
    LuaCoverageCatalog,
    LuaCoverageError,
    LuaCovStats,
    map_driver_stats,
    read_luacov_stats,
    write_luacov_stats,
)
from scripts.lua_coverage_reports import (  # noqa: E402
    build_coverage_summary,
    build_lua_coverage_report,
    read_luacov_line_report,
    write_html_report,
    write_lcov,
)


class CoverageReportingTester:
    """Exercise marker validation, stats mapping, and normalized reports."""

    def __init__(self, _xml_file=DEFAULT_XML_FILE):
        self.errors = []
        self.warnings = []
        self.test_results = []

    @staticmethod
    def _require(condition, message):
        if not condition:
            raise AssertionError(message)

    @staticmethod
    def _expect_error(operation, expected):
        try:
            operation()
        except LuaCoverageError as error:
            if expected.casefold() not in str(error).casefold():
                raise AssertionError(
                    f"Expected error containing {expected!r}, got {error!r}"
                ) from error
        else:
            raise AssertionError(f"Expected LuaCoverageError containing {expected!r}")

    @staticmethod
    def _workspace(root):
        workspace = root / "workspace"
        lua_path = workspace / "lua/fixture.lua"
        lua_path.parent.mkdir(parents=True)
        content = "local value = 1\nreturn value\n"
        lua_path.write_text(content, encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "script_count": 1,
            "scripts": [
                {
                    "script_id": "lua-0001",
                    "order": 1,
                    "source_fragment": "theGUI/src/scripts/fixture.xml",
                    "item_type": "Script",
                    "item_name": "Fixture",
                    "item_path": "ScriptGroup: Tests / Script: Fixture",
                    "lua_start_line": 9,
                    "lua_file": "lua/fixture.lua",
                    "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    "line_count": content.count("\n") + 1,
                }
            ],
        }
        (workspace / "manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )
        return workspace

    def _test_marker_and_stats_mapping(self):
        with tempfile.TemporaryDirectory(prefix="luminari-coverage-test-") as temp:
            root = Path(temp)
            workspace = self._workspace(root)
            catalog = LuaCoverageCatalog.load(workspace)
            source = catalog.source(catalog.records[0], markers_enabled=True)
            driver = f"generated = true\n{source}\nassert(generated)\n"
            drivers = root / "coverage/drivers"
            drivers.mkdir(parents=True)
            driver_path = drivers / "probe.lua"
            driver_path.write_text(driver, encoding="utf-8")

            driver_lines = driver.splitlines()
            hits = [0] * len(driver_lines)
            hits[driver_lines.index("generated = true")] = 1
            hits[driver_lines.index("local value = 1")] = 2
            hits[driver_lines.index("return value")] = 1
            raw = {str(driver_path): LuaCovStats(tuple(hits))}
            mapped, mapping = map_driver_stats(
                catalog=catalog,
                raw_stats=raw,
                drivers_dir=drivers,
                collection_cwd=root,
            )

            self._require(
                mapped["lua/fixture.lua"].hits == (2, 1),
                f"production hits were mapped incorrectly: {mapped}",
            )
            self._require(mapping["mapped_script_count"] == 1, "script was not mapped")
            self._require(
                mapping["generated_category"]["hit_line_count"] == 1,
                "generated driver hit was not kept separate",
            )
            self._require(
                all("/tmp/" not in item["driver"] for item in mapping["drivers"]),
                "mapping report leaked a temporary path",
            )

            stats_path = root / "mapped.stats.out"
            write_luacov_stats(stats_path, mapped)
            self._require(
                read_luacov_stats(stats_path) == mapped,
                "LuaCov stats did not survive a round trip",
            )

    def _test_sliced_source_maps_to_original_line(self):
        with tempfile.TemporaryDirectory(prefix="luminari-coverage-test-") as temp:
            root = Path(temp)
            catalog = LuaCoverageCatalog.load(self._workspace(root))
            full_source = catalog.source(catalog.records[0], markers_enabled=True)
            source = full_source[full_source.index("return value") :]
            driver = f"local setup = true\n{source}\n"
            drivers = root / "drivers"
            drivers.mkdir()
            driver_path = drivers / "slice.lua"
            driver_path.write_text(driver, encoding="utf-8")
            lines = driver.splitlines()
            hits = [0] * len(lines)
            hits[lines.index("return value")] = 3

            mapped, _mapping = map_driver_stats(
                catalog=catalog,
                raw_stats={str(driver_path): LuaCovStats(tuple(hits))},
                drivers_dir=drivers,
                collection_cwd=root,
            )
            self._require(
                mapped["lua/fixture.lua"].hits == (0, 3),
                "sliced production source lost its original line offset",
            )

    def _test_tampered_marker_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="luminari-coverage-test-") as temp:
            root = Path(temp)
            catalog = LuaCoverageCatalog.load(self._workspace(root))
            source = catalog.source(catalog.records[0], markers_enabled=True)
            driver = f"{source}\n".replace("local value = 1", "local value = 2")
            drivers = root / "drivers"
            drivers.mkdir()
            driver_path = drivers / "tampered.lua"
            driver_path.write_text(driver, encoding="utf-8")
            self._expect_error(
                lambda: map_driver_stats(
                    catalog=catalog,
                    raw_stats={
                        str(driver_path): LuaCovStats(
                            tuple(0 for _ in driver.splitlines())
                        )
                    },
                    drivers_dir=drivers,
                    collection_cwd=root,
                ),
                "content mismatch",
            )

    def _test_non_driver_stats_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="luminari-coverage-test-") as temp:
            root = Path(temp)
            catalog = LuaCoverageCatalog.load(self._workspace(root))
            drivers = root / "drivers"
            drivers.mkdir()
            outside = root / "outside.lua"
            outside.write_text("return true\n", encoding="utf-8")
            self._expect_error(
                lambda: map_driver_stats(
                    catalog=catalog,
                    raw_stats={str(outside): LuaCovStats((1,))},
                    drivers_dir=drivers,
                    collection_cwd=root,
                ),
                "unexpected non-driver",
            )

    def _test_normalized_reports_use_physical_xml(self):
        with tempfile.TemporaryDirectory(prefix="luminari-coverage-test-") as temp:
            root = Path(temp)
            workspace = self._workspace(root)
            catalog = LuaCoverageCatalog.load(workspace)
            line_report = root / "lines.tsv"
            line_report.write_text(
                "LUMINARI_LUACOV\t1\n"
                "F\tlua/fixture.lua\n"
                "L\t1\thit\t2\n"
                "L\t2\tmissed\t0\n"
                "S\t1\t1\n",
                encoding="utf-8",
            )
            files = read_luacov_line_report(line_report)
            report = build_lua_coverage_report(
                catalog=catalog,
                reported_files=files,
                mapping_report={
                    "mapped_script_count": 1,
                    "generated_category": {
                        "policy": "separate",
                        "line_count": 3,
                        "hit_line_count": 1,
                    },
                },
            )
            self._require(
                report["totals"]["percent_covered"] == 50.0,
                "Lua coverage percentage changed",
            )
            self._require(
                report["scripts"][0]["lines"][1]["xml_line"] == 10,
                "Lua line was not translated to its physical XML line",
            )

            lcov = root / "coverage.lcov"
            html_report = root / "index.html"
            write_lcov(lcov, report)
            write_html_report(html_report, report, catalog)
            combined = lcov.read_text() + html_report.read_text()
            self._require(
                "theGUI/src/scripts/fixture.xml" in combined,
                "normalized reports omitted the physical XML path",
            )
            self._require(
                str(root) not in combined,
                "normalized reports leaked their temporary workspace path",
            )

    def _test_separate_summary_and_deltas(self):
        lua_report = {
            "totals": {
                "covered_lines": 30,
                "num_statements": 100,
                "percent_covered": 30.0,
            },
            "generated_category": {"hit_line_count": 7},
        }
        python_report = {
            "totals": {
                "covered_lines": 80,
                "num_statements": 100,
                "percent_covered": 80.0,
            }
        }
        baseline = {
            "history": [
                {
                    "date": "2026-08-01",
                    "lua": {
                        "covered_lines": 25,
                        "num_statements": 100,
                        "percent_covered": 25.0,
                    },
                    "python": {
                        "covered_lines": 82,
                        "num_statements": 100,
                        "percent_covered": 82.0,
                    },
                }
            ]
        }
        summary, markdown = build_coverage_summary(
            lua_report=lua_report,
            python_report=python_report,
            baseline_history=baseline,
        )
        self._require(
            summary["deltas"]["lua"]["percentage_points"] == 5.0,
            "Lua delta changed",
        )
        self._require(
            summary["deltas"]["python"]["covered_lines"] == -2,
            "Python covered-line delta changed",
        )
        self._require(
            "Application Lua" in markdown and "Python tooling" in markdown,
            "summary combined or mislabeled the two coverage domains",
        )
        self._require(
            "no blocking thresholds" in markdown,
            "informational threshold policy disappeared",
        )

    def run_tests(self):
        print("Running coverage reporting regression tests...")
        tests = [
            ("marker_and_stats_mapping", self._test_marker_and_stats_mapping),
            (
                "sliced_source_line_mapping",
                self._test_sliced_source_maps_to_original_line,
            ),
            ("tampered_marker_rejected", self._test_tampered_marker_is_rejected),
            ("non_driver_stats_rejected", self._test_non_driver_stats_are_rejected),
            ("physical_xml_reports", self._test_normalized_reports_use_physical_xml),
            ("separate_summary_deltas", self._test_separate_summary_and_deltas),
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
        print(f"Coverage reporting results: {passed}/{len(tests)} passed")
        return passed == len(tests)

    def get_results(self):
        return {
            "test_results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    tester = CoverageReportingTester()
    return 0 if tester.run_tests() else 1


if __name__ == "__main__":
    raise SystemExit(main())
