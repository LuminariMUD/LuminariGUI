#!/usr/bin/env python3
"""
Lua Syntax Testing for LuminariGUI
Validates Lua code syntax using luac compiler before package creation.
"""

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


class LuaSyntaxTester:
    def __init__(self, xml_file=DEFAULT_XML_FILE):
        self.xml_file = xml_file
        self.luac_path = self._find_luac()
        self.errors = []
        self.warnings = []

    def _find_luac(self):
        """Find luac executable in system PATH."""
        for path in os.environ["PATH"].split(os.pathsep):
            for executable in ["luac", "luac5.1", "luac5.2", "luac5.3", "luac5.4"]:
                full_path = os.path.join(path, executable)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    return full_path
        return None

    def _extract_lua_scripts(self, output_dir):
        """Extract Lua once through the shared, source-mapped adapter."""
        try:
            return list(extract_for_package(self.xml_file, output_dir).scripts)
        except (FragmentBuildError, LuaExtractionError, OSError, ValueError) as error:
            self.errors.append(f"Lua extraction error: {error}")
            return []

    @staticmethod
    def _map_tool_output(script, output):
        """Translate extracted-file diagnostics back to physical XML lines."""
        path_pattern = re.compile(re.escape(str(script.output_path)) + r":(\d+):")

        def replace_line(match):
            xml_line = script.lua_start_line + int(match.group(1)) - 1
            return f"{script.source_fragment}:{xml_line}:"

        mapped = path_pattern.sub(replace_line, output)
        return mapped.replace(str(script.output_path), script.source_fragment)

    def _validate_script_syntax(self, script: ExtractedLuaScript):
        """Validate syntax of a single Lua script."""
        if not self.luac_path:
            self.errors.append("luac not found in PATH. Please install Lua compiler.")
            return False

        try:
            # Run luac -p (parse only) to check syntax
            result = subprocess.run(
                [self.luac_path, "-p", str(script.output_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True
            else:
                # Parse luac error output
                error_msg = self._map_tool_output(script, result.stderr.strip())
                self.errors.append(f"Syntax error in '{script.item_path}': {error_msg}")
                return False

        except subprocess.TimeoutExpired:
            self.errors.append(f"Timeout validating script '{script.label}'")
            return False
        except Exception as e:
            self.errors.append(f"Error validating script '{script.label}': {e}")
            return False

    def _check_common_issues(self, scripts):
        """Check for common Lua issues in the codebase."""
        issues_found = []

        for script in scripts:
            content = script.content
            name = script.label

            # Check for common issues
            if "function(" in content:
                issues_found.append(
                    f"Warning in '{name}': Missing space after 'function' keyword"
                )

            if "end)" in content and "end );" not in content:
                issues_found.append(
                    f"Warning in '{name}': 'end)' pattern may indicate missing semicolon"
                )

            # Check for HTML entities that should be unescaped
            if "&lt;" in content or "&gt;" in content or "&amp;" in content:
                issues_found.append(
                    f"Warning in '{name}': HTML entities found - may need unescaping"
                )

            # Check for potential global variable issues
            if "GUI." in content and "local GUI" not in content:
                # This is expected in this codebase, so it's just informational
                pass

        return issues_found

    def run_tests(self):
        """Run all syntax tests and return results."""
        print("Running Lua syntax validation...")

        with tempfile.TemporaryDirectory(prefix="luminari-luac-") as workspace:
            scripts = self._extract_lua_scripts(Path(workspace))
            if not scripts:
                if not self.errors:
                    self.warnings.append("No Lua scripts found in XML file")
                return False

            print(f"Found {len(scripts)} Lua scripts to validate")

            # Check syntax of each stable extracted file.
            passed = 0
            failed = 0
            for script in scripts:
                if self._validate_script_syntax(script):
                    passed += 1
                    print(f"✓ {script.label}")
                else:
                    failed += 1
                    print(f"✗ {script.label}")

            common_issues = self._check_common_issues(scripts)
            self.warnings.extend(common_issues)

        # Print summary
        print("\nSyntax validation results:")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Warnings: {len(self.warnings)}")

        # Print errors
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  {error}")

        # Print warnings
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  {warning}")

        return failed == 0

    def get_results(self):
        """Get test results for integration with other tools."""
        return {
            "passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Lua syntax in LuminariGUI XML"
    )
    parser.add_argument("--xml", default=DEFAULT_XML_FILE, help="XML file to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet mode - only errors"
    )

    args = parser.parse_args()

    tester = LuaSyntaxTester(args.xml)

    if args.quiet:
        # Suppress print statements
        import contextlib
        import io

        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            success = tester.run_tests()
    else:
        success = tester.run_tests()

    if not args.quiet and args.verbose:
        results = tester.get_results()
        print(f"\nDetailed results: {results}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
