#!/usr/bin/env python3
"""Normalize Lua-tool reports back to physical XML fragments and item paths."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


class DiagnosticMappingError(RuntimeError):
    """Raised when a tool diagnostic cannot be mapped unambiguously."""


@dataclass(frozen=True)
class ScriptOrigin:
    lua_file: str
    source_fragment: str
    item_path: str
    lua_start_line: int


class ManifestSourceMap:
    """Resolve stable or temporary tool paths through an extraction manifest."""

    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path.resolve()
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise DiagnosticMappingError(
                f"Could not read extraction manifest {manifest_path}: {error}"
            ) from error

        if manifest.get("schema_version") != 1:
            raise DiagnosticMappingError("Unsupported extraction manifest schema")
        self.origins = {
            item["lua_file"]: ScriptOrigin(
                lua_file=item["lua_file"],
                source_fragment=item["source_fragment"],
                item_path=item["item_path"],
                lua_start_line=item["lua_start_line"],
            )
            for item in manifest.get("scripts", [])
        }
        if not self.origins:
            raise DiagnosticMappingError("Extraction manifest contains no Lua scripts")

    def resolve(self, reported_path: str) -> ScriptOrigin:
        parsed = urlparse(reported_path)
        if parsed.scheme == "file":
            normalized = unquote(parsed.path)
        else:
            normalized = reported_path
        normalized = normalized.replace("\\", "/").removeprefix("./")

        direct_candidates = [normalized]
        path = Path(normalized)
        if path.is_absolute():
            try:
                direct_candidates.append(
                    path.resolve().relative_to(self.manifest_path.parent).as_posix()
                )
            except ValueError:
                pass
        for candidate in direct_candidates:
            if candidate in self.origins:
                return self.origins[candidate]

        suffix_matches = [
            origin
            for lua_file, origin in self.origins.items()
            if normalized == lua_file or normalized.endswith(f"/{lua_file}")
        ]
        if len(suffix_matches) == 1:
            return suffix_matches[0]
        if not suffix_matches:
            raise DiagnosticMappingError(
                f"Tool path is absent from extraction manifest: {reported_path}"
            )
        raise DiagnosticMappingError(f"Tool path maps ambiguously: {reported_path}")

    @staticmethod
    def finding(
        *,
        tool: str,
        origin: ScriptOrigin,
        lua_line: int,
        column: int,
        code: str,
        severity: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        finding = {
            "tool": tool,
            "code": code,
            "severity": severity,
            "message": message,
            "source_fragment": origin.source_fragment,
            "item_path": origin.item_path,
            "source_line": origin.lua_start_line + lua_line - 1,
            "source_column": column,
            "lua_file": origin.lua_file,
            "lua_line": lua_line,
        }
        if details:
            finding["details"] = details
        return finding


def remap_luals(report: dict[str, Any], source_map: ManifestSourceMap):
    severity_names = {1: "error", 2: "warning", 3: "information", 4: "hint"}
    findings = []
    for reported_path, diagnostics in report.items():
        origin = source_map.resolve(reported_path)
        for diagnostic in diagnostics:
            start = diagnostic.get("range", {}).get("start", {})
            severity_number = int(diagnostic.get("severity", 2))
            findings.append(
                source_map.finding(
                    tool="luals",
                    origin=origin,
                    lua_line=int(start.get("line", 0)) + 1,
                    column=int(start.get("character", 0)) + 1,
                    code=str(diagnostic.get("code", "diagnostic")),
                    severity=severity_names.get(severity_number, "unknown"),
                    message=str(diagnostic.get("message", "LuaLS diagnostic")),
                )
            )
    return findings, []


def remap_semgrep(report: dict[str, Any], source_map: ManifestSourceMap):
    findings = []
    for result in report.get("results", []):
        origin = source_map.resolve(result["path"])
        start = result.get("start", {})
        extra = result.get("extra", {})
        findings.append(
            source_map.finding(
                tool="semgrep",
                origin=origin,
                lua_line=int(start.get("line", 1)),
                column=int(start.get("col", 1)),
                code=str(result.get("check_id", "semgrep")),
                severity=str(extra.get("severity", "WARNING")).casefold(),
                message=str(extra.get("message", "Semgrep finding")),
            )
        )
    return findings, report.get("errors", [])


def remap_stylua(report: list[dict[str, Any]], source_map: ManifestSourceMap):
    findings = []
    for result in report:
        origin = source_map.resolve(result["file"])
        mismatches = result.get("mismatches", [])
        if not mismatches:
            continue
        first_line = min(
            int(mismatch.get("original_start_line", 1)) for mismatch in mismatches
        )
        findings.append(
            source_map.finding(
                tool="stylua",
                origin=origin,
                lua_line=first_line,
                column=1,
                code="format",
                severity="information",
                message=f"StyLua would reformat {len(mismatches)} range(s)",
                details={"mismatch_count": len(mismatches)},
            )
        )
    return findings, []


def load_report(path: Path, tool: str):
    try:
        content = path.read_text(encoding="utf-8")
        if tool == "stylua":
            return [json.loads(line) for line in content.splitlines() if line.strip()]
        return json.loads(content)
    except (OSError, json.JSONDecodeError) as error:
        raise DiagnosticMappingError(
            f"Could not read {tool} report {path}: {error}"
        ) from error


def normalize_report(
    *,
    tool: str,
    manifest_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    source_map = ManifestSourceMap(manifest_path)
    report = load_report(report_path, tool)
    if tool == "luals":
        findings, tool_errors = remap_luals(report, source_map)
    elif tool == "semgrep":
        findings, tool_errors = remap_semgrep(report, source_map)
    elif tool == "stylua":
        findings, tool_errors = remap_stylua(report, source_map)
    else:
        raise DiagnosticMappingError(f"Unsupported tool: {tool}")

    severity_counts: dict[str, int] = {}
    for finding in findings:
        severity = finding["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    return {
        "schema_version": 1,
        "tool": tool,
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "tool_error_count": len(tool_errors),
        "tool_errors": tool_errors,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Map LuaLS, StyLua, or Semgrep results to physical XML sources"
    )
    parser.add_argument("--tool", choices=("luals", "stylua", "semgrep"), required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        normalized = normalize_report(
            tool=args.tool,
            manifest_path=args.manifest,
            report_path=args.input,
        )
        args.output.write_text(
            json.dumps(normalized, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (DiagnosticMappingError, OSError, ValueError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"Mapped {normalized['finding_count']} {args.tool} finding(s); "
        f"tool errors: {normalized['tool_error_count']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
