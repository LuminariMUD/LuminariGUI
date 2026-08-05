#!/usr/bin/env python3
"""Command-line entry point for source-aware coverage mapping and reports."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lua_coverage import (  # noqa: E402
    LuaCoverageCatalog,
    LuaCoverageError,
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


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise LuaCoverageError(f"Could not read JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise LuaCoverageError(f"Expected a JSON object in {path}")
    return value


def _command_map(args: argparse.Namespace) -> None:
    catalog = LuaCoverageCatalog.load(args.workspace)
    raw_stats = read_luacov_stats(args.raw_stats)
    mapped, mapping = map_driver_stats(
        catalog=catalog,
        raw_stats=raw_stats,
        drivers_dir=args.drivers,
        collection_cwd=args.collection_cwd,
    )
    write_luacov_stats(args.output_stats, mapped)
    args.output_map.parent.mkdir(parents=True, exist_ok=True)
    args.output_map.write_text(
        json.dumps(mapping, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _command_render(args: argparse.Namespace) -> None:
    catalog = LuaCoverageCatalog.load(args.workspace)
    files = read_luacov_line_report(args.line_report)
    mapping = _load_json(args.mapping)
    report = build_lua_coverage_report(
        catalog=catalog,
        reported_files=files,
        mapping_report=mapping,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_lcov(args.output_lcov, report)
    write_html_report(args.output_html, report, catalog)


def _command_summary(args: argparse.Namespace) -> None:
    baseline = _load_json(args.baseline) if args.baseline else None
    summary, markdown = build_coverage_summary(
        lua_report=_load_json(args.lua),
        python_report=_load_json(args.python),
        baseline_history=baseline,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_markdown.write_text(markdown, encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Map and render source-aware Lua/Python coverage reports"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    mapping = commands.add_parser("map", help="map raw driver stats to extracted Lua")
    mapping.add_argument("--workspace", type=Path, required=True)
    mapping.add_argument("--raw-stats", type=Path, required=True)
    mapping.add_argument("--drivers", type=Path, required=True)
    mapping.add_argument("--collection-cwd", type=Path, default=Path.cwd())
    mapping.add_argument("--output-stats", type=Path, required=True)
    mapping.add_argument("--output-map", type=Path, required=True)
    mapping.set_defaults(operation=_command_map)

    render = commands.add_parser("render", help="render normalized Lua reports")
    render.add_argument("--workspace", type=Path, required=True)
    render.add_argument("--line-report", type=Path, required=True)
    render.add_argument("--mapping", type=Path, required=True)
    render.add_argument("--output-json", type=Path, required=True)
    render.add_argument("--output-lcov", type=Path, required=True)
    render.add_argument("--output-html", type=Path, required=True)
    render.set_defaults(operation=_command_render)

    summary = commands.add_parser("summary", help="summarize separate coverage totals")
    summary.add_argument("--lua", type=Path, required=True)
    summary.add_argument("--python", type=Path, required=True)
    summary.add_argument("--baseline", type=Path)
    summary.add_argument("--output-json", type=Path, required=True)
    summary.add_argument("--output-markdown", type=Path, required=True)
    summary.set_defaults(operation=_command_summary)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        args.operation(args)
    except (LuaCoverageError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
