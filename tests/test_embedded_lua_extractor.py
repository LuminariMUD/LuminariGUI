#!/usr/bin/env python3
"""Regression tests for the shared embedded-Lua extraction bridge."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XML_FILE = str(PROJECT_ROOT / "LuminariGUI.xml")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.extract_embedded_lua import (  # noqa: E402
    EmbeddedLuaExtractor,
    LuaExtractionError,
    extract_for_package,
)
from scripts.remap_lua_diagnostics import (  # noqa: E402
    DiagnosticMappingError,
    normalize_report,
)
from theGUI.build import FragmentBuildError, FragmentValidator  # noqa: E402


class EmbeddedLuaExtractorTester:
    """Exercise ordering, decoding, source mapping, and write safety."""

    def __init__(self, xml_file=DEFAULT_XML_FILE):
        self.xml_file = Path(xml_file).resolve()
        self.errors = []
        self.warnings = []
        self.test_results = []

    @staticmethod
    def _require(condition, message):
        if not condition:
            raise AssertionError(message)

    @staticmethod
    def _hash_files(paths):
        return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}

    @staticmethod
    def _expect_extraction_error(operation, expected_text):
        try:
            operation()
        except (FragmentBuildError, LuaExtractionError) as error:
            if expected_text.casefold() not in str(error).casefold():
                raise AssertionError(
                    f"Expected error containing {expected_text!r}, got {error!r}"
                ) from error
        else:
            raise AssertionError(
                f"Expected extraction error containing {expected_text!r}"
            )

    def _write_fixture(self, root):
        thegui = root / "theGUI"
        triggers = thegui / "src/triggers"
        scripts = thegui / "src/scripts"
        triggers.mkdir(parents=True)
        scripts.mkdir(parents=True)

        config = thegui / "build.yaml"
        config.write_text(
            """package:
  name: "Fixture"
  version: "1.0.0"
output:
  file: "../Fixture.xml"
  encoding: "UTF-8"
options:
  embed_markers: false
  validate_fragments: true
  validate_output: true
  strip_dev_comments: true
triggers:
  - src/triggers/root.xml
aliases: []
scripts:
  - src/scripts/multiple.xml
keys: []
""",
            encoding="utf-8",
        )
        root_fragment = triggers / "root.xml"
        root_fragment.write_text(
            """<TriggerGroup isActive="yes" isFolder="yes">
  <name>Parent &amp; Co</name>
  <packageName></packageName>
  <script></script>
  <eventHandlerList />
  <!-- BUILD_INCLUDE: child.xml -->
  <!-- BUILD_INCLUDE: child.xml -->
  <Trigger isActive="yes" isFolder="no">
    <name>Same Name</name>
    <packageName></packageName>
    <script>local entity = "A &amp; B"
return 1 &lt; 2</script>
    <eventHandlerList />
  </Trigger>
</TriggerGroup>
""",
            encoding="utf-8",
        )
        child_fragment = triggers / "child.xml"
        child_fragment.write_text(
            """<Trigger isActive="yes" isFolder="no">
  <name>Same Name</name>
  <packageName></packageName>
  <script>return "child &amp; decoded"</script>
  <eventHandlerList />
</Trigger>
""",
            encoding="utf-8",
        )
        multiple_fragment = scripts / "multiple.xml"
        multiple_fragment.write_text(
            """<ScriptGroup isActive="yes" isFolder="yes">
  <name>Multiple</name>
  <packageName></packageName>
  <script>local first = true</script>
  <eventHandlerList />
  <Script isActive="yes" isFolder="no">
    <name>Second</name>
    <packageName></packageName>
    <script>return first</script>
    <eventHandlerList />
  </Script>
</ScriptGroup>
""",
            encoding="utf-8",
        )
        return config, (root_fragment, child_fragment, multiple_fragment)

    def _test_fixture_extraction(self):
        with tempfile.TemporaryDirectory(prefix="luminari-extractor-fixture-") as temp:
            root = Path(temp)
            config, fragments = self._write_fixture(root)
            before = self._hash_files((config, *fragments))
            result = EmbeddedLuaExtractor(root).extract_project(
                root / "workspace", config
            )
            after = self._hash_files((config, *fragments))

            self._require(before == after, "extraction modified its physical inputs")
            self._require(result.mode == "project", "project mode was not recorded")
            self._require(len(result.sources) == 4, "composite source count changed")
            self._require(len(result.scripts) == 5, "nonempty script count changed")
            self._require(
                result.empty_script_count == 1, "empty script was not counted"
            )

            contents = [script.content for script in result.scripts]
            self._require(
                contents
                == [
                    'return "child & decoded"',
                    'return "child & decoded"',
                    'local entity = "A & B"\nreturn 1 < 2',
                    "local first = true",
                    "return first",
                ],
                f"decoded assembly order changed: {contents!r}",
            )
            self._require(
                result.scripts[0].item_path
                == "TriggerGroup: Parent & Co / Trigger: Same Name",
                "include-site ancestry was not preserved",
            )
            self._require(
                result.scripts[0].source_occurrence == 1
                and result.scripts[1].source_occurrence == 2,
                "duplicate includes were not assigned stable occurrences",
            )

            lua_files = [script.lua_file for script in result.scripts]
            self._require(
                len(lua_files) == len(set(lua_files)),
                "duplicate item names collided in the output workspace",
            )
            self._require(
                all(
                    script.output_path.read_text() == script.content
                    for script in result.scripts
                ),
                "materialized Lua differs from decoded content",
            )
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            self._require(manifest["schema_version"] == 1, "manifest schema changed")
            self._require(manifest["script_count"] == 5, "manifest count is stale")
            self._require(
                all("source_fragment" in item for item in manifest["scripts"]),
                "manifest omitted physical source paths",
            )

            repeated = EmbeddedLuaExtractor(root).extract_project(
                root / "repeated-workspace", config
            )
            self._require(
                [script.lua_file for script in repeated.scripts] == lua_files,
                "extracted filenames were not stable across runs",
            )

    def _test_current_package_parity(self):
        with tempfile.TemporaryDirectory(prefix="luminari-extractor-parity-") as temp:
            tracked_inputs = sorted((PROJECT_ROOT / "theGUI/src").rglob("*.xml"))
            if self.xml_file.is_relative_to(PROJECT_ROOT):
                tracked_inputs.extend(
                    [PROJECT_ROOT / "theGUI/build.yaml", self.xml_file]
                )
            before = self._hash_files(tracked_inputs)
            result = extract_for_package(self.xml_file, Path(temp) / "workspace")
            after = self._hash_files(tracked_inputs)
            self._require(
                before == after, "package extraction modified source fragments"
            )

            root = ET.parse(self.xml_file).getroot()
            assembled = [
                element.text
                for element in root.iter("script")
                if element.text and element.text.strip()
            ]
            extracted = [script.content for script in result.scripts]
            self._require(
                extracted == assembled,
                "shared extraction is not byte-for-byte equivalent to package order",
            )
            self._require(
                len({script.lua_file for script in result.scripts}) == len(extracted),
                "current package generated colliding Lua paths",
            )
            if result.mode == "project":
                self._require(
                    {script.section for script in result.scripts}
                    == {"triggers", "aliases", "scripts", "keys"},
                    "one or more build-manifest sections were not extracted",
                )
            self._require(
                all(
                    script.lua_start_line >= script.xml_script_line
                    for script in result.scripts
                ),
                "source line mapping moved before an opening <script> tag",
            )

    def _test_duplicate_name_scopes(self):
        def package(trigger_items):
            return f"""<?xml version="1.0" encoding="UTF-8"?>
<MudletPackage version="1">
  <TriggerPackage>{trigger_items}</TriggerPackage>
  <AliasPackage>
    <Alias><name>Shared</name></Alias>
  </AliasPackage>
  <ScriptPackage>
    <ScriptGroup><name>Shared</name>
      <Script><name>Shared</name></Script>
    </ScriptGroup>
  </ScriptPackage>
  <KeyPackage>
    <Key><name>Shared</name></Key>
  </KeyPackage>
</MudletPackage>
"""

        allowed = package(
            """
    <TriggerGroup><name>First</name>
      <Trigger><name>Shared</name></Trigger>
    </TriggerGroup>
    <TriggerGroup><name>Second</name>
      <Trigger><name>Shared</name></Trigger>
    </TriggerGroup>
    <Trigger><name>Case</name></Trigger>
    <Trigger><name>case</name></Trigger>
"""
        )
        valid, errors = FragmentValidator.validate_final_xml(allowed)
        self._require(
            valid and not errors,
            f"valid cross-scope Mudlet names were rejected: {errors}",
        )

        sibling_collision = package(
            """
    <TriggerGroup><name>Parent</name>
      <Trigger><name>Same</name></Trigger>
      <TriggerGroup><name>Same</name></TriggerGroup>
    </TriggerGroup>
"""
        )
        valid, errors = FragmentValidator.validate_final_xml(sibling_collision)
        self._require(not valid, "same-family sibling collision was accepted")
        self._require(
            len(errors) == 1
            and "TriggerPackage / TriggerGroup 'Parent'" in errors[0]
            and "duplicate Trigger name 'Same'" in errors[0]
            and "Trigger and TriggerGroup" in errors[0],
            f"sibling collision diagnostic lost its Mudlet scope: {errors}",
        )

        current = self.xml_file.read_text(encoding="utf-8")
        valid, errors = FragmentValidator.validate_final_xml(current)
        self._require(
            valid and not errors,
            f"current intentional cross-scope names were rejected: {errors}",
        )

    def _test_arbitrary_xml_mode(self):
        with tempfile.TemporaryDirectory(prefix="luminari-extractor-xml-") as temp:
            root = Path(temp)
            xml_path = root / "custom.xml"
            xml_path.write_text(
                """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE MudletPackage>
<MudletPackage version="1">
  <ScriptPackage>
    <Script isActive="yes" isFolder="no">
      <name>Custom</name>
      <script>
return "A &amp; B"
      </script>
      <eventHandlerList />
    </Script>
  </ScriptPackage>
</MudletPackage>
""",
                encoding="utf-8",
            )
            result = EmbeddedLuaExtractor(root).extract_xml(
                xml_path, root / "workspace"
            )
            self._require(result.mode == "xml", "XML mode was not recorded")
            self._require(len(result.scripts) == 1, "custom XML script was missed")
            self._require(
                result.scripts[0].content == '\nreturn "A & B"\n      ',
                "custom XML entities or whitespace were not preserved",
            )
            self._require(
                result.scripts[0].lua_start_line == 7,
                "custom XML Lua start line was mapped incorrectly",
            )

    def _test_diagnostic_remapping(self):
        with tempfile.TemporaryDirectory(prefix="luminari-diagnostic-map-") as temp:
            root = Path(temp)
            config, _fragments = self._write_fixture(root)
            result = EmbeddedLuaExtractor(root).extract_project(
                root / "workspace", config
            )
            script = result.scripts[0]

            luals_path = root / "luals.json"
            luals_path.write_text(
                json.dumps(
                    {
                        script.output_path.as_uri(): [
                            {
                                "code": "undefined-global",
                                "message": "Undefined global `unsafe`.",
                                "range": {
                                    "start": {"line": 0, "character": 2},
                                    "end": {"line": 0, "character": 8},
                                },
                                "severity": 2,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            luals = normalize_report(
                tool="luals",
                manifest_path=result.manifest_path,
                report_path=luals_path,
            )
            finding = luals["findings"][0]
            self._require(
                finding["source_fragment"] == script.source_fragment
                and finding["item_path"] == script.item_path
                and finding["source_line"] == script.lua_start_line,
                "LuaLS diagnostic did not map to its XML item and line",
            )
            self._require(
                str(root) not in json.dumps(luals),
                "normalized LuaLS report retained a random temporary path",
            )

            semgrep_path = root / "semgrep.json"
            semgrep_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "check_id": "fixture.rule",
                                "path": f"/src/{script.lua_file}",
                                "start": {"line": 1, "col": 1},
                                "extra": {"severity": "ERROR", "message": "fixture"},
                            }
                        ],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            semgrep = normalize_report(
                tool="semgrep",
                manifest_path=result.manifest_path,
                report_path=semgrep_path,
            )
            self._require(
                semgrep["findings"][0]["source_line"] == script.lua_start_line,
                "Semgrep suffix path was not mapped",
            )

            stylua_path = root / "stylua.jsonl"
            stylua_path.write_text(
                json.dumps(
                    {
                        "file": str(script.output_path),
                        "mismatches": [
                            {
                                "original_start_line": 1,
                                "original_end_line": 1,
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            stylua = normalize_report(
                tool="stylua",
                manifest_path=result.manifest_path,
                report_path=stylua_path,
            )
            self._require(
                stylua["findings"][0]["item_path"] == script.item_path,
                "StyLua diagnostic did not map to its Mudlet item",
            )

            missing_path = root / "missing.json"
            missing_path.write_text(
                json.dumps({"file:///not/extracted.lua": []}), encoding="utf-8"
            )
            try:
                normalize_report(
                    tool="luals",
                    manifest_path=result.manifest_path,
                    report_path=missing_path,
                )
            except DiagnosticMappingError:
                pass
            else:
                raise AssertionError("unmapped diagnostic path was accepted")

    def _test_malformed_and_traversal_rejected(self):
        with tempfile.TemporaryDirectory(prefix="luminari-extractor-invalid-") as temp:
            root = Path(temp)
            config, fragments = self._write_fixture(root)
            fragments[0].write_text("<TriggerGroup><name>broken</TriggerGroup>")
            self._expect_extraction_error(
                lambda: EmbeddedLuaExtractor(root).extract_project(
                    root / "malformed-output", config
                ),
                "parse error",
            )

        with tempfile.TemporaryDirectory(
            prefix="luminari-extractor-traversal-"
        ) as temp:
            root = Path(temp)
            config, fragments = self._write_fixture(root)
            fragments[0].write_text(
                """<TriggerGroup>
  <name>Traversal</name>
  <script></script>
  <!-- BUILD_INCLUDE: ../../outside.xml -->
</TriggerGroup>
""",
                encoding="utf-8",
            )
            (root / "theGUI/outside.xml").write_text(
                "<Trigger><name>Outside</name><script>return true</script></Trigger>",
                encoding="utf-8",
            )
            self._expect_extraction_error(
                lambda: EmbeddedLuaExtractor(root).extract_project(
                    root / "traversal-output", config
                ),
                "escapes the source tree",
            )

    def _test_output_safety(self):
        with tempfile.TemporaryDirectory(prefix="luminari-extractor-safety-") as temp:
            root = Path(temp)
            config, _fragments = self._write_fixture(root)
            nonempty = root / "nonempty"
            nonempty.mkdir()
            sentinel = nonempty / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            self._expect_extraction_error(
                lambda: EmbeddedLuaExtractor(root).extract_project(nonempty, config),
                "must be empty",
            )
            self._require(sentinel.read_text() == "keep", "nonempty output was changed")

            protected = root / "theGUI/src/generated"
            self._expect_extraction_error(
                lambda: EmbeddedLuaExtractor(root).extract_project(protected, config),
                "protected source path",
            )
            self._require(
                not protected.exists(), "protected output directory was created"
            )

            class CollidingExtractor(EmbeddedLuaExtractor):
                def _lua_file(self, *_args):
                    return "lua/collision.lua"

            collision_output = root / "collision-output"
            self._expect_extraction_error(
                lambda: CollidingExtractor(root).extract_project(
                    collision_output, config
                ),
                "collision",
            )
            self._require(
                not collision_output.exists(),
                "collision validation left a partial workspace",
            )

            class TraversingExtractor(EmbeddedLuaExtractor):
                def _lua_file(self, *_args):
                    return "../escaped.lua"

            traversal_output = root / "output-path-traversal"
            self._expect_extraction_error(
                lambda: TraversingExtractor(root).extract_project(
                    traversal_output, config
                ),
                "escapes output workspace",
            )
            self._require(
                not (root / "escaped.lua").exists(),
                "output traversal wrote outside the workspace",
            )

    def run_tests(self):
        print("Running embedded-Lua extractor regressions...")
        checks = [
            ("fixture ordering and mapping", self._test_fixture_extraction),
            ("assembled-package parity", self._test_current_package_parity),
            ("Mudlet duplicate-name scopes", self._test_duplicate_name_scopes),
            ("arbitrary XML mode", self._test_arbitrary_xml_mode),
            ("tool diagnostic remapping", self._test_diagnostic_remapping),
            (
                "malformed/traversal rejection",
                self._test_malformed_and_traversal_rejected,
            ),
            ("output workspace safety", self._test_output_safety),
        ]

        for name, check in checks:
            try:
                check()
            except Exception as error:
                self.errors.append(f"{name}: {error}")
                self.test_results.append({"name": name, "passed": False})
                print(f"✗ {name}: {error}")
            else:
                self.test_results.append({"name": name, "passed": True})
                print(f"✓ {name}")

        return not self.errors

    def get_results(self):
        return {
            "passed": not self.errors,
            "checks": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    tester = EmbeddedLuaExtractorTester()
    success = tester.run_tests()
    if not success:
        print("\nErrors:")
        for error in tester.errors:
            print(f"  {error}")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
