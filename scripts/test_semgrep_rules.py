#!/usr/bin/env python3
"""Verify every LuminariGUI Lua Semgrep rule with positive/negative fixtures."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RULE_IDS = {
    "luminari.lua.dynamic-code-execution",
    "luminari.lua.sensitive-runtime-logging",
    "luminari.lua.shell-execution",
    "luminari.lua.string-code-callback",
    "luminari.lua.untrusted-command-flow",
    "luminari.lua.untrusted-file-path-flow",
    "luminari.lua.untrusted-rich-output-flow",
}


class SemgrepFixtureError(RuntimeError):
    """Raised when rule execution or fixture expectations fail."""


def _run_scan(executable: str, config: Path, target: Path):
    result = subprocess.run(
        [
            executable,
            "scan",
            "--config",
            str(config),
            "--json",
            "--metrics=off",
            "--quiet",
            str(target),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise SemgrepFixtureError(
            f"Semgrep failed for {target}: {result.stdout}\n{result.stderr}"
        )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SemgrepFixtureError(
            f"Semgrep returned invalid JSON for {target}: {error}"
        ) from error
    if report.get("errors"):
        raise SemgrepFixtureError(
            f"Semgrep reported errors for {target}: {report['errors']}"
        )
    return report


def _canonical_rule_id(check_id: str) -> str:
    marker = "luminari.lua."
    index = check_id.find(marker)
    return check_id[index:] if index >= 0 else check_id


def validate_fixtures(
    *,
    executable: str,
    config: Path,
    positive: Path,
    negative: Path,
) -> dict[str, int]:
    positive_report = _run_scan(executable, config, positive)
    negative_report = _run_scan(executable, config, negative)

    positive_ids = [
        _canonical_rule_id(result["check_id"])
        for result in positive_report.get("results", [])
    ]
    missing = EXPECTED_RULE_IDS - set(positive_ids)
    unexpected = set(positive_ids) - EXPECTED_RULE_IDS
    duplicates = {
        rule_id: positive_ids.count(rule_id)
        for rule_id in set(positive_ids)
        if positive_ids.count(rule_id) != 1
    }
    if missing or unexpected or duplicates:
        raise SemgrepFixtureError(
            "Positive fixture mismatch: "
            f"missing={sorted(missing)}, unexpected={sorted(unexpected)}, "
            f"counts={duplicates}"
        )

    negative_ids = [
        _canonical_rule_id(result["check_id"])
        for result in negative_report.get("results", [])
    ]
    if negative_ids:
        raise SemgrepFixtureError(
            f"Negative fixture produced findings: {sorted(negative_ids)}"
        )
    return {
        "rules": len(EXPECTED_RULE_IDS),
        "positive_findings": len(positive_ids),
        "negative_findings": len(negative_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semgrep", default="semgrep", help="Semgrep executable")
    parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "semgrep/rules/luminari-lua-security.yml",
    )
    parser.add_argument(
        "--positive",
        type=Path,
        default=PROJECT_ROOT / "semgrep/fixtures/positive.lua",
    )
    parser.add_argument(
        "--negative",
        type=Path,
        default=PROJECT_ROOT / "semgrep/fixtures/negative.lua",
    )
    args = parser.parse_args()

    try:
        results = validate_fixtures(
            executable=args.semgrep,
            config=args.config,
            positive=args.positive,
            negative=args.negative,
        )
    except (OSError, SemgrepFixtureError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"Semgrep fixtures passed: {results['rules']} rules, "
        f"{results['positive_findings']} positive findings, "
        f"{results['negative_findings']} negative findings"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
