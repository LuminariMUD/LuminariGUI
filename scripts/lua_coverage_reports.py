#!/usr/bin/env python3
"""Render normalized Lua coverage and split Lua/Python summaries."""

from __future__ import annotations

import html
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.lua_coverage import LuaCoverageCatalog, LuaCoverageError


@dataclass(frozen=True)
class ReportedLine:
    """One LuaCov reporter classification for a stable extracted Lua line."""

    line: int
    status: str
    hits: int


@dataclass(frozen=True)
class ReportedFile:
    """LuaCov reporter output for one stable extracted file."""

    filename: str
    lines: tuple[ReportedLine, ...]
    covered_lines: int
    missed_lines: int


def read_luacov_line_report(path: Path) -> dict[str, ReportedFile]:
    """Read the checked-in Luminari LuaCov reporter's TSV protocol."""
    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise LuaCoverageError(f"Could not read LuaCov line report: {error}") from error
    if not raw_lines or raw_lines[0] != "LUMINARI_LUACOV\t1":
        raise LuaCoverageError("Unsupported LuaCov line-report schema")

    files: dict[str, ReportedFile] = {}
    filename: str | None = None
    lines: list[ReportedLine] = []
    covered = missed = 0

    def finish_file() -> None:
        nonlocal filename, lines, covered, missed
        if filename is None:
            return
        if filename in files:
            raise LuaCoverageError(f"Duplicate LuaCov report path: {filename}")
        expected_lines = list(range(1, len(lines) + 1))
        actual_lines = [line.line for line in lines]
        if actual_lines != expected_lines:
            raise LuaCoverageError(
                f"LuaCov report lines are not contiguous for {filename}"
            )
        actual_covered = sum(line.status == "hit" for line in lines)
        actual_missed = sum(line.status == "missed" for line in lines)
        if (covered, missed) != (actual_covered, actual_missed):
            raise LuaCoverageError(
                f"LuaCov report summary mismatch for {filename}: "
                f"expected {(actual_covered, actual_missed)}, "
                f"found {(covered, missed)}"
            )
        files[filename] = ReportedFile(
            filename=filename,
            lines=tuple(lines),
            covered_lines=covered,
            missed_lines=missed,
        )
        filename = None
        lines = []
        covered = missed = 0

    for raw_line in raw_lines[1:]:
        fields = raw_line.split("\t")
        kind = fields[0]
        if kind == "F" and len(fields) == 2:
            finish_file()
            filename = fields[1].removeprefix("./")
        elif kind == "L" and len(fields) == 4 and filename is not None:
            try:
                line_number = int(fields[1])
                hits = int(fields[3])
            except ValueError as error:
                raise LuaCoverageError(
                    f"Malformed LuaCov line record: {raw_line}"
                ) from error
            status = fields[2]
            if status not in {"hit", "missed", "excluded"}:
                raise LuaCoverageError(f"Unknown LuaCov line status: {status}")
            lines.append(ReportedLine(line_number, status, hits))
        elif kind == "S" and len(fields) == 3 and filename is not None:
            try:
                covered, missed = int(fields[1]), int(fields[2])
            except ValueError as error:
                raise LuaCoverageError(
                    f"Malformed LuaCov summary: {raw_line}"
                ) from error
            finish_file()
        elif raw_line:
            raise LuaCoverageError(f"Malformed LuaCov line-report record: {raw_line}")
    finish_file()
    return files


def _percent(covered: int, total: int) -> float:
    return round((covered / total * 100.0) if total else 100.0, 2)


def build_lua_coverage_report(
    *,
    catalog: LuaCoverageCatalog,
    reported_files: Mapping[str, ReportedFile],
    mapping_report: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a normalized report containing only tracked physical XML paths."""
    expected = {record.lua_file for record in catalog.records}
    actual = set(reported_files)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise LuaCoverageError(
            f"LuaCov reporter/source-map mismatch; missing={missing}, extra={extra}"
        )

    scripts: list[dict[str, Any]] = []
    total_covered = total_missed = 0
    for record in catalog.records:
        reported = reported_files[record.lua_file]
        if len(reported.lines) != record.report_line_count:
            raise LuaCoverageError(
                f"LuaCov reporter line count mismatch for {record.lua_file}"
            )
        covered = reported.covered_lines
        missed = reported.missed_lines
        total_covered += covered
        total_missed += missed
        scripts.append(
            {
                "script_id": record.script_id,
                "source_fragment": record.source_fragment,
                "item_type": record.item_type,
                "item_name": record.item_name,
                "item_path": record.item_path,
                "lua_start_line": record.lua_start_line,
                "totals": {
                    "covered_lines": covered,
                    "missed_lines": missed,
                    "num_statements": covered + missed,
                    "percent_covered": _percent(covered, covered + missed),
                },
                "lines": [
                    {
                        "lua_line": line.line,
                        "xml_line": record.lua_start_line + line.line - 1,
                        "status": line.status,
                        "hits": line.hits,
                    }
                    for line in reported.lines
                ],
            }
        )

    total = total_covered + total_missed
    return {
        "schema_version": 1,
        "kind": "application-lua",
        "tool": "LuaCov",
        "tool_version": "0.17.0",
        "scope": "production Lua executed by mock-based lifecycle tests",
        "threshold_policy": "informational; no blocking threshold",
        "totals": {
            "covered_lines": total_covered,
            "missed_lines": total_missed,
            "num_statements": total,
            "percent_covered": _percent(total_covered, total),
        },
        "mapped_script_count": mapping_report["mapped_script_count"],
        "production_script_count": len(catalog.records),
        "generated_category": mapping_report["generated_category"],
        "scripts": scripts,
    }


def write_lcov(path: Path, report: Mapping[str, Any]) -> None:
    """Write physical XML line coverage in LCOV's machine-readable format."""
    output: list[str] = []
    for script in report["scripts"]:
        output.append(f"TN:{script['item_path']}")
        output.append(f"SF:{script['source_fragment']}")
        hit_lines = 0
        found_lines = 0
        for line in script["lines"]:
            if line["status"] == "excluded":
                continue
            found_lines += 1
            if line["hits"] > 0:
                hit_lines += 1
            output.append(f"DA:{line['xml_line']},{line['hits']}")
        output.extend([f"LF:{found_lines}", f"LH:{hit_lines}", "end_of_record"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def write_html_report(
    path: Path,
    report: Mapping[str, Any],
    catalog: LuaCoverageCatalog,
) -> None:
    """Write a self-contained HTML report labeled with physical XML origins."""
    by_id = catalog.by_id
    totals = report["totals"]
    rows: list[str] = []
    details: list[str] = []
    for script in report["scripts"]:
        script_totals = script["totals"]
        location = f"{script['source_fragment']}:{script['lua_start_line']}"
        rows.append(
            "<tr>"
            f'<td><a href="#{html.escape(script["script_id"])}">'
            f"{html.escape(script['item_path'])}</a></td>"
            f"<td>{html.escape(location)}</td>"
            f"<td>{script_totals['covered_lines']}</td>"
            f"<td>{script_totals['missed_lines']}</td>"
            f"<td>{script_totals['percent_covered']:.2f}%</td>"
            "</tr>"
        )

        record = by_id[script["script_id"]]
        source_lines = record.content.splitlines()
        code_rows: list[str] = []
        for line, source in zip(script["lines"], source_lines, strict=True):
            css_class = line["status"]
            hits = "" if line["status"] == "excluded" else str(line["hits"])
            code_rows.append(
                f'<tr class="{css_class}"><td>{line["xml_line"]}</td>'
                f"<td>{html.escape(hits)}</td>"
                f"<td><pre>{html.escape(source)}</pre></td></tr>"
            )
        details.append(
            f'<details id="{html.escape(script["script_id"])}">'
            f"<summary>{html.escape(script['item_path'])} — "
            f"{script_totals['percent_covered']:.2f}%</summary>"
            f'<p>{html.escape(location)}</p><table class="code"><tbody>'
            + "".join(code_rows)
            + "</tbody></table></details>"
        )

    generated = report["generated_category"]
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LuminariGUI Lua coverage</title>
<style>
body{{font:14px system-ui,sans-serif;max-width:1200px;margin:2rem auto;padding:0 1rem;color:#172033}}
h1,h2{{color:#111827}}table{{border-collapse:collapse;width:100%;margin:1rem 0}}
th,td{{border:1px solid #d7dce5;padding:.4rem .55rem;text-align:left;vertical-align:top}}
th{{background:#eef2f7}}pre{{margin:0;white-space:pre-wrap;font:12px ui-monospace,monospace}}
.hit{{background:#e8f8ee}}.missed{{background:#ffe9e8}}.excluded{{color:#7b8495}}
details{{margin:1rem 0}}summary{{cursor:pointer;font-weight:650}}
.metric{{display:inline-block;background:#eef2ff;padding:.55rem .8rem;margin:.2rem;border-radius:.4rem}}
</style></head><body>
<h1>Application Lua coverage</h1>
<p>Production Lua exercised by mock-based lifecycle tests. This informational report does not replace Mudlet runtime smoke testing.</p>
<div class="metric"><strong>{totals["percent_covered"]:.2f}%</strong> covered</div>
<div class="metric"><strong>{totals["covered_lines"]}</strong> hit lines</div>
<div class="metric"><strong>{totals["missed_lines"]}</strong> missed lines</div>
<div class="metric"><strong>{report["mapped_script_count"]}/{report["production_script_count"]}</strong> scripts mapped</div>
<p>Generated driver code is excluded from production totals and reported separately: {generated["hit_line_count"]} hit lines across {generated["line_count"]} generated lines.</p>
<h2>Scripts</h2><table><thead><tr><th>Item</th><th>Physical XML</th><th>Hit</th><th>Missed</th><th>Coverage</th></tr></thead><tbody>
{"".join(rows)}</tbody></table><h2>Line detail</h2>{"".join(details)}
</body></html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def _coverage_metrics(report: Mapping[str, Any]) -> dict[str, float | int]:
    totals = report["totals"]
    covered_lines = int(totals["covered_lines"])
    statement_count = int(totals["num_statements"])
    return {
        "covered_lines": covered_lines,
        "num_statements": statement_count,
        "percent_covered": _percent(covered_lines, statement_count),
    }


def build_coverage_summary(
    *,
    lua_report: Mapping[str, Any],
    python_report: Mapping[str, Any],
    baseline_history: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], str]:
    """Keep Python tooling and application Lua totals visibly independent."""
    current = {
        "lua": _coverage_metrics(lua_report),
        "python": _coverage_metrics(python_report),
    }
    baseline = None
    if baseline_history is not None:
        history = baseline_history.get("history")
        if not isinstance(history, list) or not history:
            raise LuaCoverageError("Coverage baseline history is empty or malformed")
        baseline = history[-1]

    def format_line(label: str, key: str) -> str:
        metrics = current[key]
        detail = (
            f"{metrics['covered_lines']}/{metrics['num_statements']} lines "
            f"({metrics['percent_covered']:.2f}%)"
        )
        if baseline is None:
            return f"- {label}: {detail}; first baseline pending"
        old = baseline[key]
        point_delta = metrics["percent_covered"] - float(old["percent_covered"])
        line_delta = metrics["covered_lines"] - int(old["covered_lines"])
        return (
            f"- {label}: {detail}; delta {point_delta:+.2f} percentage points, "
            f"{line_delta:+d} covered lines vs {baseline['date']}"
        )

    generated = lua_report["generated_category"]
    markdown = "\n".join(
        [
            "### Coverage (informational)",
            "",
            format_line("Application Lua", "lua"),
            format_line("Python tooling", "python"),
            (
                "- Generated Lua drivers: excluded from production totals; "
                f"{generated['hit_line_count']} hit lines reported separately"
            ),
            "- Thresholds: no blocking thresholds while baseline history is collected",
            "",
        ]
    )
    summary = {
        "schema_version": 1,
        "threshold_policy": "informational; no blocking thresholds",
        "current": current,
        "baseline": baseline,
        "deltas": (
            None
            if baseline is None
            else {
                key: {
                    "covered_lines": current[key]["covered_lines"]
                    - int(baseline[key]["covered_lines"]),
                    "percentage_points": round(
                        current[key]["percent_covered"]
                        - float(baseline[key]["percent_covered"]),
                        2,
                    ),
                }
                for key in ("lua", "python")
            }
        ),
    }
    return summary, markdown
