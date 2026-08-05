#!/usr/bin/env python3
"""Extract Mudlet's embedded Lua into a stable, source-mapped workspace.

The normal mode reads ``theGUI/build.yaml`` and follows the same composite
fragment rules as the package builder.  ``--xml`` is available for validating
an arbitrary, already assembled Mudlet package.  Neither mode modifies its
inputs; the output directory must be absent or empty.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import xml.parsers.expat
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from theGUI.build import (  # noqa: E402
    BUILD_INCLUDE_PATTERN,
    BuildConfig,
    CompositeFragmentResolver,
    FragmentBuildError,
    FragmentValidator,
)

INCLUDE_ELEMENT = "LuminariBuildInclude"
ITEM_TAGS = {
    "Action",
    "ActionGroup",
    "Alias",
    "AliasGroup",
    "Key",
    "KeyGroup",
    "Script",
    "ScriptGroup",
    "Timer",
    "TimerGroup",
    "Trigger",
    "TriggerGroup",
}
SECTION_NAMES = ("triggers", "aliases", "scripts", "keys")


class LuaExtractionError(RuntimeError):
    """Raised when a safe, complete extraction cannot be produced."""


@dataclass(frozen=True)
class SourceOccurrence:
    """One physical fragment occurrence in assembled package order."""

    source_id: str
    source_fragment: str
    source_occurrence: int
    entry_fragment: str
    section: str
    entry_index: int
    include_depth: int


@dataclass(frozen=True)
class ExtractedLuaScript:
    """A decoded Lua block and its physical XML origin."""

    script_id: str
    order: int
    source_id: str
    source_fragment: str
    source_occurrence: int
    entry_fragment: str
    section: str
    entry_index: int
    include_depth: int
    item_type: str
    item_name: str
    item_path: str
    xml_script_line: int
    lua_start_line: int
    lua_file: str
    sha256: str
    byte_count: int
    line_count: int
    content: str
    output_path: Path

    @property
    def origin(self) -> str:
        """Return a human-readable physical source location."""
        return f"{self.source_fragment}:{self.lua_start_line}"

    @property
    def label(self) -> str:
        """Return an item path paired with its physical source location."""
        return f"{self.item_path} ({self.origin})"

    def manifest_record(self) -> dict[str, Any]:
        """Return the stable, JSON-safe part of this record."""
        record = asdict(self)
        record.pop("content")
        record.pop("output_path")
        return record


@dataclass(frozen=True)
class ExtractionResult:
    """The materialized workspace and source map."""

    output_dir: Path
    manifest_path: Path
    sources: tuple[SourceOccurrence, ...]
    scripts: tuple[ExtractedLuaScript, ...]
    empty_script_count: int
    mode: str


@dataclass
class _SourceContext:
    source: SourceOccurrence
    path: Path
    raw_content: str
    locators: list[tuple[int, int]]
    locator_index: int = 0

    def next_locator(self) -> tuple[int, int]:
        if self.locator_index >= len(self.locators):
            raise LuaExtractionError(
                f"Could not map every <script> in {self.source.source_fragment}"
            )
        locator = self.locators[self.locator_index]
        self.locator_index += 1
        return locator


def _local_name(tag: str) -> str:
    """Remove an optional ElementTree namespace from a tag."""
    return tag.rsplit("}", 1)[-1]


def _slug(value: str, fallback: str) -> str:
    """Create a predictable, traversal-safe path component."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or fallback


def _project_relative(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.name


def _script_locations(content: str, *, fragment: bool) -> list[tuple[int, int]]:
    """Locate opening tags and the XML line corresponding to Lua line one."""
    prefix = b"<LuminariExtractionRoot>" if fragment else b""
    suffix = b"</LuminariExtractionRoot>" if fragment else b""
    raw = content.encode("utf-8")
    document = prefix + raw + suffix
    locations: list[tuple[int, int]] = []
    parser = xml.parsers.expat.ParserCreate()

    def start_element(name: str, _attributes: dict[str, str]) -> None:
        if _local_name(name) != "script":
            return

        raw_offset = parser.CurrentByteIndex - len(prefix)
        if raw_offset < 0 or raw_offset >= len(raw):
            raise LuaExtractionError("Internal XML source mapping offset was invalid")

        quote: int | None = None
        tag_end = raw_offset
        while tag_end < len(raw):
            byte = raw[tag_end]
            if quote is not None:
                if byte == quote:
                    quote = None
            elif byte in (ord('"'), ord("'")):
                quote = byte
            elif byte == ord(">"):
                break
            tag_end += 1
        else:
            raise LuaExtractionError("Unterminated <script> opening tag")

        xml_line = raw.count(b"\n", 0, raw_offset) + 1
        lua_start_line = raw.count(b"\n", 0, tag_end + 1) + 1
        locations.append((xml_line, lua_start_line))

    parser.StartElementHandler = start_element
    try:
        parser.Parse(document, True)
    except xml.parsers.expat.ExpatError as error:
        raise LuaExtractionError(f"XML source mapping failed: {error}") from error
    return locations


class EmbeddedLuaExtractor:
    """Build a stable Lua workspace from source fragments or one XML file."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = project_root.resolve()
        self._sources: list[SourceOccurrence] = []
        self._scripts: list[ExtractedLuaScript] = []
        self._source_counts: dict[str, int] = {}
        self._empty_script_count = 0
        self._output_dir = self.project_root

    def extract_project(
        self,
        output_dir: Path,
        config_path: Path | None = None,
    ) -> ExtractionResult:
        """Extract all nonempty scripts selected by a build manifest."""
        config_path = (config_path or self.project_root / "theGUI/build.yaml").resolve()
        config = BuildConfig(config_path)
        source_root = config_path.parent / "src"
        resolver = CompositeFragmentResolver(
            source_root,
            FragmentValidator(),
            validate_fragments=config.validate_fragments,
            strip_dev_comments=config.strip_dev_comments,
        )
        output = self._prepare(output_dir, protected_root=source_root)

        for section in SECTION_NAMES:
            entries = getattr(config, section)
            for entry_index, entry in enumerate(entries, start=1):
                entry_path = config_path.parent / entry
                _expanded, physical_sources = resolver.resolve(entry_path)
                source_content = {
                    display: content for display, content, _depth in physical_sources
                }
                entry_fragment = _project_relative(entry_path, self.project_root)
                top_display = resolver.display_path(entry_path.resolve())
                self._walk_fragment(
                    path=entry_path.resolve(),
                    raw_content=source_content[top_display],
                    source_content=source_content,
                    resolver=resolver,
                    entry_fragment=entry_fragment,
                    section=section,
                    entry_index=entry_index,
                    include_depth=0,
                    ancestry=(),
                )

        return self._materialize(output, mode="project", config_path=config_path)

    def extract_xml(self, xml_path: Path, output_dir: Path) -> ExtractionResult:
        """Extract nonempty scripts from an arbitrary assembled package."""
        xml_path = xml_path.resolve()
        if not xml_path.is_file():
            raise LuaExtractionError(f"XML file not found: {xml_path}")
        try:
            content = xml_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise LuaExtractionError(
                f"XML file is not valid UTF-8: {xml_path}"
            ) from error

        try:
            root = ET.fromstring(content)
        except ET.ParseError as error:
            raise LuaExtractionError(
                f"XML parse error in {xml_path}: {error}"
            ) from error

        output = self._prepare(output_dir, protected_root=xml_path)
        source_fragment = _project_relative(xml_path, self.project_root)
        source = self._new_source(
            source_fragment=source_fragment,
            entry_fragment=source_fragment,
            section="package",
            entry_index=1,
            include_depth=0,
        )
        context = _SourceContext(
            source=source,
            path=xml_path,
            raw_content=content,
            locators=_script_locations(content, fragment=False),
        )
        self._walk_element(root, context, ancestry=())
        self._assert_all_locators_used(context)
        return self._materialize(output, mode="xml", config_path=None)

    def _prepare(self, output_dir: Path, protected_root: Path) -> Path:
        if self._sources or self._scripts:
            raise LuaExtractionError("An extractor instance can only be used once")

        output = output_dir.resolve()
        protected = protected_root.resolve()
        try:
            output.relative_to(protected)
        except ValueError:
            pass
        else:
            raise LuaExtractionError(
                f"Output workspace cannot be inside protected source path: {protected}"
            )

        if output.exists():
            if not output.is_dir():
                raise LuaExtractionError(f"Output path is not a directory: {output}")
            if next(output.iterdir(), None) is not None:
                raise LuaExtractionError(f"Output directory must be empty: {output}")
        self._output_dir = output
        return output

    def _walk_fragment(
        self,
        *,
        path: Path,
        raw_content: str,
        source_content: dict[str, str],
        resolver: CompositeFragmentResolver,
        entry_fragment: str,
        section: str,
        entry_index: int,
        include_depth: int,
        ancestry: tuple[str, ...],
    ) -> None:
        include_refs: list[str] = []

        def replace_include(match: re.Match[str]) -> str:
            include_id = len(include_refs)
            include_refs.append(match.group("path").strip())
            newline = match.group("newline")
            return (
                f'{match.group("indent")}<{INCLUDE_ELEMENT} id="{include_id}" />'
                f"{newline}"
            )

        parseable = BUILD_INCLUDE_PATTERN.sub(replace_include, raw_content)
        try:
            root = ET.fromstring(
                f"<LuminariExtractionRoot>{parseable}</LuminariExtractionRoot>"
            )
        except ET.ParseError as error:
            display = resolver.display_path(path)
            raise LuaExtractionError(
                f"Could not parse validated fragment {display}: {error}"
            ) from error

        source_fragment = _project_relative(path, self.project_root)
        source = self._new_source(
            source_fragment=source_fragment,
            entry_fragment=entry_fragment,
            section=section,
            entry_index=entry_index,
            include_depth=include_depth,
        )
        context = _SourceContext(
            source=source,
            path=path,
            raw_content=raw_content,
            locators=_script_locations(raw_content, fragment=True),
        )

        def include_callback(
            element: ET.Element, item_ancestry: tuple[str, ...]
        ) -> None:
            try:
                include_ref = include_refs[int(element.attrib["id"])]
            except (KeyError, ValueError, IndexError) as error:
                raise LuaExtractionError(
                    f"Invalid internal include marker in {source_fragment}"
                ) from error
            child_path = (path.parent / include_ref).resolve()
            display = resolver.display_path(child_path)
            try:
                child_content = source_content[display]
            except KeyError as error:
                raise LuaExtractionError(
                    f"Validated include missing from source map: {display}"
                ) from error
            self._walk_fragment(
                path=child_path,
                raw_content=child_content,
                source_content=source_content,
                resolver=resolver,
                entry_fragment=entry_fragment,
                section=section,
                entry_index=entry_index,
                include_depth=include_depth + 1,
                ancestry=item_ancestry,
            )

        self._walk_element(root, context, ancestry, include_callback)
        self._assert_all_locators_used(context)

    def _walk_element(
        self,
        element: ET.Element,
        context: _SourceContext,
        ancestry: tuple[str, ...],
        include_callback: Any | None = None,
    ) -> None:
        tag = _local_name(element.tag)
        item_ancestry = ancestry
        if tag in ITEM_TAGS:
            name_element = next(
                (child for child in element if _local_name(child.tag) == "name"),
                None,
            )
            name = (
                "".join(name_element.itertext()).strip()
                if name_element is not None
                else ""
            )
            item_ancestry += (f"{tag}: {name or 'unnamed'}",)

        for child in element:
            child_tag = _local_name(child.tag)
            if child_tag == "script":
                self._record_script(child, context, item_ancestry, tag)
            elif child_tag == INCLUDE_ELEMENT:
                if include_callback is None:
                    raise LuaExtractionError("Unexpected build include marker")
                include_callback(child, item_ancestry)
            else:
                self._walk_element(
                    child,
                    context,
                    item_ancestry,
                    include_callback,
                )

    def _record_script(
        self,
        script_element: ET.Element,
        context: _SourceContext,
        ancestry: tuple[str, ...],
        parent_tag: str,
    ) -> None:
        xml_line, lua_start_line = context.next_locator()
        content = script_element.text or ""
        if not content.strip():
            self._empty_script_count += 1
            return

        item_path = " / ".join(ancestry) if ancestry else f"{parent_tag}: unnamed"
        last_item = ancestry[-1] if ancestry else f"{parent_tag}: unnamed"
        item_type, _, item_name = last_item.partition(": ")
        order = len(self._scripts) + 1
        lua_file = self._lua_file(context.source, order, item_type, item_name)
        encoded = content.encode("utf-8")
        self._scripts.append(
            ExtractedLuaScript(
                script_id=f"lua-{order:04d}",
                order=order,
                source_id=context.source.source_id,
                source_fragment=context.source.source_fragment,
                source_occurrence=context.source.source_occurrence,
                entry_fragment=context.source.entry_fragment,
                section=context.source.section,
                entry_index=context.source.entry_index,
                include_depth=context.source.include_depth,
                item_type=item_type,
                item_name=item_name,
                item_path=item_path,
                xml_script_line=xml_line,
                lua_start_line=lua_start_line,
                lua_file=lua_file,
                sha256=hashlib.sha256(encoded).hexdigest(),
                byte_count=len(encoded),
                line_count=content.count("\n") + 1,
                content=content,
                output_path=self._output_dir / lua_file,
            )
        )

    def _new_source(
        self,
        *,
        source_fragment: str,
        entry_fragment: str,
        section: str,
        entry_index: int,
        include_depth: int,
    ) -> SourceOccurrence:
        occurrence = self._source_counts.get(source_fragment, 0) + 1
        self._source_counts[source_fragment] = occurrence
        source = SourceOccurrence(
            source_id=f"source-{len(self._sources) + 1:04d}",
            source_fragment=source_fragment,
            source_occurrence=occurrence,
            entry_fragment=entry_fragment,
            section=section,
            entry_index=entry_index,
            include_depth=include_depth,
        )
        self._sources.append(source)
        return source

    def _lua_file(
        self,
        source: SourceOccurrence,
        order: int,
        item_type: str,
        item_name: str,
    ) -> str:
        source_path = Path(source.source_fragment)
        safe_parts = [
            _slug(part, "source") for part in source_path.with_suffix("").parts
        ]
        folder = Path("lua", *safe_parts, f"occurrence-{source.source_occurrence:03d}")
        filename = (
            f"{order:04d}-{_slug(item_type, 'item')}-{_slug(item_name, 'unnamed')}.lua"
        )
        return (folder / filename).as_posix()

    @staticmethod
    def _assert_all_locators_used(context: _SourceContext) -> None:
        if context.locator_index != len(context.locators):
            raise LuaExtractionError(
                "XML parser/source mapper script count mismatch in "
                f"{context.source.source_fragment}: parsed {context.locator_index}, "
                f"located {len(context.locators)}"
            )

    def _materialize(
        self,
        output: Path,
        *,
        mode: str,
        config_path: Path | None,
    ) -> ExtractionResult:
        planned: set[Path] = set()
        output_resolved = output.resolve()
        for script in self._scripts:
            destination = script.output_path.resolve()
            try:
                destination.relative_to(output_resolved)
            except ValueError as error:
                raise LuaExtractionError(
                    f"Extracted Lua path escapes output workspace: {script.lua_file}"
                ) from error
            if destination in planned:
                raise LuaExtractionError(
                    f"Extracted Lua path collision: {script.lua_file}"
                )
            planned.add(destination)

        output.mkdir(parents=True, exist_ok=True)
        for script in self._scripts:
            script.output_path.parent.mkdir(parents=True, exist_ok=True)
            script.output_path.write_text(script.content, encoding="utf-8")

        manifest = {
            "schema_version": 1,
            "mode": mode,
            "config": (
                _project_relative(config_path, self.project_root)
                if config_path is not None
                else None
            ),
            "source_count": len(self._sources),
            "script_count": len(self._scripts),
            "empty_script_count": self._empty_script_count,
            "sources": [asdict(source) for source in self._sources],
            "scripts": [script.manifest_record() for script in self._scripts],
        }
        manifest_path = output / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return ExtractionResult(
            output_dir=output,
            manifest_path=manifest_path,
            sources=tuple(self._sources),
            scripts=tuple(self._scripts),
            empty_script_count=self._empty_script_count,
            mode=mode,
        )


def extract_for_package(
    xml_file: str | Path,
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> ExtractionResult:
    """Use physical sources for the canonical package, otherwise use one XML."""
    root = Path(project_root).resolve()
    xml_path = Path(xml_file).resolve()
    extractor = EmbeddedLuaExtractor(root)
    if xml_path == (root / "LuminariGUI.xml").resolve():
        return extractor.extract_project(Path(output_dir))
    return extractor.extract_xml(xml_path, Path(output_dir))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract embedded Lua into a stable, source-mapped workspace"
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Absent or empty directory to receive lua/ and manifest.json",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root (default: inferred from this script)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Build manifest (default: <project-root>/theGUI/build.yaml)",
    )
    parser.add_argument(
        "--xml",
        type=Path,
        help="Extract one assembled XML file instead of build-manifest sources",
    )
    args = parser.parse_args()

    try:
        extractor = EmbeddedLuaExtractor(args.project_root)
        if args.xml is not None:
            if args.config is not None:
                parser.error("--config and --xml are mutually exclusive")
            result = extractor.extract_xml(args.xml, args.output)
        else:
            result = extractor.extract_project(args.output, args.config)
    except (FragmentBuildError, LuaExtractionError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"Extracted {len(result.scripts)} nonempty Lua scripts from "
        f"{len(result.sources)} source occurrence(s)"
    )
    print(f"Manifest: {result.manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
