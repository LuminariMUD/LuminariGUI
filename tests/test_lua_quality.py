#!/usr/bin/env python3
"""
Lua Quality Analysis for LuminariGUI
Static analysis using luacheck to find code quality issues.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XML_FILE = str(PROJECT_ROOT / "LuminariGUI.xml")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.extract_embedded_lua import (  # noqa: E402
    ExtractedLuaScript,
    LuaExtractionError,
    extract_for_package,
)
from theGUI.build import FragmentBuildError  # noqa: E402


class LuaQualityAnalyzer:
    def __init__(self, xml_file=DEFAULT_XML_FILE):
        self.xml_file = xml_file
        self.luacheck_path = self._find_luacheck()
        self.errors = []
        self.warnings = []
        self.issues = []

    def _find_luacheck(self):
        """Find luacheck executable in system PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            luacheck_path = os.path.join(path, "luacheck")
            if os.path.isfile(luacheck_path) and os.access(luacheck_path, os.X_OK):
                return luacheck_path
        return None

    def _extract_lua_scripts(self, output_dir):
        """Extract Lua once through the shared, source-mapped adapter."""
        try:
            return list(extract_for_package(self.xml_file, output_dir).scripts)
        except (FragmentBuildError, LuaExtractionError, OSError, ValueError) as error:
            self.errors.append(f"Lua extraction error: {error}")
            return []

    def _get_luacheck_config(self):
        """Get the path to the luacheck configuration file."""
        # Check if custom config exists
        config_path = (
            Path(__file__).resolve().parent / "test_configs/luacheck_config.lua"
        )
        if config_path.exists():
            return str(config_path)

        # Fallback to creating a temporary config
        self.warnings.append(
            "Using fallback luacheck configuration. Consider using test_configs/luacheck_config.lua"
        )
        config_content = """
-- Fallback Mudlet/LuminariGUI configuration
std = "luajit"
globals = {
    "cecho", "decho", "echo", "send",
    "raiseEvent", "registerAnonymousEventHandler",
    "msdp", "gmcp", "mud", "matches",
    "Geyser", "geyser",
    "GUI", "LUM", "map", "demonnic"
}
ignore = {
    "212", "213", "311", "411", "412", "421", "422", "542", "614"
}
"""

        config_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".luacheckrc", delete=False
        )
        config_file.write(config_content)
        config_file.close()
        return config_file.name

    def _analyze_script(self, script: ExtractedLuaScript):
        """Analyze a single Lua script with luacheck."""
        if not self.luacheck_path:
            self.errors.append("luacheck not found in PATH. Please install luacheck.")
            return False

        config_file_path = self._get_luacheck_config()

        try:
            # Run luacheck without JSON formatter (use default output)
            result = subprocess.run(
                [
                    self.luacheck_path,
                    "--config",
                    config_file_path,
                    str(script.output_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                # No issues found
                return True
            elif result.returncode == 1:
                # Issues found, parse default output
                # Default luacheck output format:
                # filename:line:column: message
                for line in result.stdout.strip().split("\n"):
                    if (
                        line
                        and ":" in line
                        and not line.startswith("Checking")
                        and not line.startswith("Total:")
                    ):
                        # Parse line like: test.lua:3:5: setting non-standard global variable 'unused_global'
                        match = re.match(r"^\s*([^:]+):(\d+):(\d+):\s*(.+)$", line)
                        if match:
                            _, line_num, col_num, message = match.groups()
                            # Determine severity based on message content
                            if "error" in message.lower():
                                severity = "error"
                                code = "E"
                            else:
                                severity = "warning"
                                code = "W"

                            self.issues.append(
                                {
                                    "script": script.item_path,
                                    "source": script.source_fragment,
                                    "line": int(line_num),
                                    "xml_line": script.lua_start_line
                                    + int(line_num)
                                    - 1,
                                    "column": int(col_num),
                                    "code": code,
                                    "message": message.strip(),
                                    "severity": severity,
                                }
                            )
                return False
            else:
                # luacheck error
                self.errors.append(
                    f"luacheck error for '{script.label}': {result.stderr}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.errors.append(f"Timeout analyzing script '{script.label}'")
            return False
        except Exception as e:
            self.errors.append(f"Error analyzing script '{script.label}': {e}")
            return False
        finally:
            # Only delete a generated fallback configuration.
            try:
                if config_file_path and not config_file_path.endswith(
                    "luacheck_config.lua"
                ):
                    os.unlink(config_file_path)
            except OSError:
                pass

    def _categorize_issues(self):
        """Categorize issues by severity and type."""
        categorized = {"critical": [], "errors": [], "warnings": [], "style": []}

        for issue in self.issues:
            code = issue["code"]
            # Critical issues (undefined access)
            if code in ["111", "112", "113", "142", "143", "321"]:
                categorized["critical"].append(issue)
            # Errors (logic problems)
            elif code in ["511", "512", "521", "531", "541"]:
                categorized["errors"].append(issue)
            # Warnings (potential issues)
            elif code in ["311", "312", "551"]:
                categorized["warnings"].append(issue)
            # Style issues
            elif code in ["611", "612", "613", "631"]:
                categorized["style"].append(issue)
            else:
                # Default to warnings
                categorized["warnings"].append(issue)

        return categorized

    def run_analysis(self):
        """Run quality analysis on all scripts."""
        print("Running Lua quality analysis...")

        if not self.luacheck_path:
            print("luacheck not found. Please install luacheck:")
            print("  Ubuntu/Debian: sudo apt-get install luacheck")
            print("  macOS: brew install luacheck")
            print("  Other: luarocks install luacheck")
            return False

        with tempfile.TemporaryDirectory(prefix="luminari-luacheck-") as workspace:
            scripts = self._extract_lua_scripts(Path(workspace))
            if not scripts:
                if not self.errors:
                    self.warnings.append("No Lua scripts found in XML file")
                return False

            print(f"Found {len(scripts)} Lua scripts to analyze")

            # Analyze each stable extracted file.
            passed = 0
            failed = 0
            for script in scripts:
                if self._analyze_script(script):
                    passed += 1
                    print(f"✓ {script.label}")
                else:
                    failed += 1
                    print(f"⚠ {script.label}")

        # Categorize and display results
        categorized = self._categorize_issues()

        print("\nQuality analysis results:")
        print(f"  Scripts analyzed: {len(scripts)}")
        print(f"  Clean scripts: {passed}")
        print(f"  Scripts with issues: {failed}")
        print(f"  Total issues: {len(self.issues)}")

        # Display issues by category
        for category, issues in categorized.items():
            if issues:
                print(f"\n{category.upper()} ({len(issues)} issues):")
                for issue in issues:
                    print(
                        f"  {issue['source']}:{issue['xml_line']}:{issue['column']} "
                        f"({issue['script']}) - {issue['message']}"
                    )

        # Display errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")

        return len(categorized["critical"]) == 0 and len(categorized["errors"]) == 0

    def get_results(self):
        """Get analysis results for integration with other tools."""
        categorized = self._categorize_issues()
        return {
            "passed": len(categorized["critical"]) == 0
            and len(categorized["errors"]) == 0,
            "issues": categorized,
            "total_issues": len(self.issues),
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze Lua code quality in LuminariGUI XML"
    )
    parser.add_argument("--xml", default=DEFAULT_XML_FILE, help="XML file to analyze")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet mode - only errors"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    analyzer = LuaQualityAnalyzer(args.xml)

    if args.quiet:
        # Suppress print statements
        import contextlib
        import io

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = analyzer.run_analysis()
    else:
        success = analyzer.run_analysis()

    if args.json:
        results = analyzer.get_results()
        print(json.dumps(results, indent=2))

    if not args.quiet and args.verbose:
        results = analyzer.get_results()
        print(f"\nDetailed results: {results}")

    # Apply strict mode
    if args.strict:
        results = analyzer.get_results()
        success = success and results["total_issues"] == 0

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
