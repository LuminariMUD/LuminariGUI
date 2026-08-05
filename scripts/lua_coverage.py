#!/usr/bin/env python3
"""Source-aware LuaCov support for embedded Mudlet Lua.

Lifecycle tests execute production snippets inside generated Lua drivers so
their local Mudlet mocks remain visible.  This module marks those snippets,
maps driver line hits back onto the shared extracted Lua workspace, and keeps
generated test code out of the production coverage totals.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class LuaCoverageError(RuntimeError):
    """Raised when coverage data cannot be mapped without ambiguity."""


@dataclass(frozen=True)
class LuaScriptRecord:
    """One stable extracted script and its physical XML origin."""

    script_id: str
    order: int
    source_fragment: str
    item_type: str
    item_name: str
    item_path: str
    lua_start_line: int
    lua_file: str
    sha256: str
    line_count: int
    content: str
    output_path: Path

    @property
    def report_line_count(self) -> int:
        """Return the physical lines LuaCov's reporter reads from the file."""
        return len(self.content.splitlines())

    @classmethod
    def from_manifest(
        cls,
        workspace: Path,
        raw: Mapping[str, Any],
    ) -> LuaScriptRecord:
        required = {
            "script_id",
            "order",
            "source_fragment",
            "item_type",
            "item_name",
            "item_path",
            "lua_start_line",
            "lua_file",
            "sha256",
            "line_count",
        }
        missing = sorted(required.difference(raw))
        if missing:
            raise LuaCoverageError(
                "Coverage manifest record is missing: " + ", ".join(missing)
            )

        lua_file = str(raw["lua_file"])
        relative_path = Path(lua_file)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise LuaCoverageError(f"Unsafe extracted Lua path: {lua_file}")
        output_path = (workspace / relative_path).resolve()
        try:
            output_path.relative_to(workspace.resolve())
        except ValueError as error:
            raise LuaCoverageError(
                f"Extracted Lua path escapes its workspace: {lua_file}"
            ) from error
        if not output_path.is_file():
            raise LuaCoverageError(f"Extracted Lua file is missing: {lua_file}")

        content = output_path.read_text(encoding="utf-8")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if digest != raw["sha256"]:
            raise LuaCoverageError(f"Extracted Lua hash mismatch: {lua_file}")
        line_count = content.count("\n") + 1
        if line_count != raw["line_count"]:
            raise LuaCoverageError(f"Extracted Lua line count mismatch: {lua_file}")

        source_fragment = str(raw["source_fragment"])
        source_path = Path(source_fragment)
        if source_path.is_absolute() or ".." in source_path.parts:
            raise LuaCoverageError(
                f"Unsafe physical source path in manifest: {source_fragment}"
            )

        return cls(
            script_id=str(raw["script_id"]),
            order=int(raw["order"]),
            source_fragment=source_fragment,
            item_type=str(raw["item_type"]),
            item_name=str(raw["item_name"]),
            item_path=str(raw["item_path"]),
            lua_start_line=int(raw["lua_start_line"]),
            lua_file=relative_path.as_posix(),
            sha256=str(raw["sha256"]),
            line_count=line_count,
            content=content,
            output_path=output_path,
        )


class MarkedLuaSource(str):
    """A string that emits inert source markers when interpolated into Lua."""

    record: LuaScriptRecord
    start_offset: int
    markers_enabled: bool

    def __new__(
        cls,
        content: str,
        record: LuaScriptRecord,
        *,
        start_offset: int = 0,
        markers_enabled: bool = False,
    ) -> MarkedLuaSource:
        instance = super().__new__(cls, content)
        instance.record = record
        instance.start_offset = start_offset
        instance.markers_enabled = markers_enabled
        return instance

    def __getitem__(self, key: int | slice) -> str | MarkedLuaSource:
        value = super().__getitem__(key)
        if not isinstance(key, slice):
            return value

        start, _stop, step = key.indices(len(self))
        if step != 1:
            return value
        return MarkedLuaSource(
            value,
            self.record,
            start_offset=self.start_offset + start,
            markers_enabled=self.markers_enabled,
        )

    def __format__(self, format_spec: str) -> str:
        if format_spec:
            return str.__format__(str(self), format_spec)
        if not self.markers_enabled:
            return str(self)

        content = str(self)
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        begin = (
            "-- LUMINARI_COVERAGE_BEGIN "
            f"script={self.record.script_id} offset={self.start_offset} "
            f"length={len(content)} sha256={digest}"
        )
        end = f"-- LUMINARI_COVERAGE_END script={self.record.script_id} sha256={digest}"
        separator = "" if content.endswith("\n") else "\n"
        return f"{begin}\n{content}{separator}{end}"


class LuaCoverageCatalog:
    """Validated access to one shared embedded-Lua extraction workspace."""

    def __init__(self, workspace: Path, records: Sequence[LuaScriptRecord]):
        self.workspace = workspace.resolve()
        self.records = tuple(records)
        self.by_id = {record.script_id: record for record in self.records}
        if len(self.by_id) != len(self.records):
            raise LuaCoverageError("Coverage manifest contains duplicate script IDs")

    @classmethod
    def load(cls, workspace: Path) -> LuaCoverageCatalog:
        workspace = workspace.resolve()
        manifest_path = workspace / "manifest.json"
        if not manifest_path.is_file():
            raise LuaCoverageError(
                f"Coverage workspace has no manifest.json: {workspace}"
            )
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            raise LuaCoverageError(
                f"Could not read coverage manifest: {error}"
            ) from error
        if manifest.get("schema_version") != 1:
            raise LuaCoverageError("Unsupported embedded-Lua manifest schema")
        raw_scripts = manifest.get("scripts")
        if not isinstance(raw_scripts, list):
            raise LuaCoverageError("Coverage manifest scripts must be a list")
        records = [LuaScriptRecord.from_manifest(workspace, raw) for raw in raw_scripts]
        if len(records) != manifest.get("script_count"):
            raise LuaCoverageError("Coverage manifest script count is inconsistent")
        return cls(workspace, records)

    def source(
        self,
        record: LuaScriptRecord,
        *,
        markers_enabled: bool,
    ) -> MarkedLuaSource:
        return MarkedLuaSource(
            record.content,
            record,
            markers_enabled=markers_enabled,
        )

    def find(
        self,
        *,
        source_fragment: str | None = None,
        item_name: str | None = None,
        item_path: str | None = None,
        content: str | None = None,
    ) -> LuaScriptRecord:
        candidates = [
            record
            for record in self.records
            if (source_fragment is None or record.source_fragment == source_fragment)
            and (item_name is None or record.item_name == item_name)
            and (item_path is None or record.item_path == item_path)
            and (content is None or record.content == content)
        ]
        if len(candidates) != 1:
            criteria = {
                "source_fragment": source_fragment,
                "item_name": item_name,
                "item_path": item_path,
                "content": "<provided>" if content is not None else None,
            }
            raise LuaCoverageError(
                f"Expected one extracted Lua match, found {len(candidates)}: {criteria}"
            )
        return candidates[0]


@dataclass(frozen=True)
class LuaCovStats:
    """LuaCov line-hit data for one source path."""

    hits: tuple[int, ...]

    def hit(self, line: int) -> int:
        if line < 1 or line > len(self.hits):
            return 0
        return self.hits[line - 1]


def read_luacov_stats(path: Path) -> dict[str, LuaCovStats]:
    """Read LuaCov 0.17's documented text stats representation."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise LuaCoverageError(f"Could not read LuaCov stats: {error}") from error

    parsed: dict[str, LuaCovStats] = {}
    index = 0
    while index < len(lines):
        header = lines[index]
        index += 1
        if ":" not in header:
            raise LuaCoverageError(f"Malformed LuaCov stats header: {header!r}")
        maximum_text, filename = header.split(":", 1)
        try:
            maximum = int(maximum_text)
        except ValueError as error:
            raise LuaCoverageError(
                f"Malformed LuaCov maximum line: {maximum_text!r}"
            ) from error
        if maximum < 0 or not filename:
            raise LuaCoverageError(f"Malformed LuaCov stats header: {header!r}")
        if index >= len(lines):
            raise LuaCoverageError(f"LuaCov stats are missing hits for {filename}")
        try:
            hits = tuple(int(value) for value in lines[index].split())
        except ValueError as error:
            raise LuaCoverageError(f"Malformed LuaCov hits for {filename}") from error
        index += 1
        if len(hits) != maximum or any(value < 0 for value in hits):
            raise LuaCoverageError(
                f"LuaCov hit count length mismatch for {filename}: "
                f"expected {maximum}, found {len(hits)}"
            )
        if filename in parsed:
            raise LuaCoverageError(f"Duplicate LuaCov stats path: {filename}")
        parsed[filename] = LuaCovStats(hits)
    return parsed


def write_luacov_stats(path: Path, stats: Mapping[str, LuaCovStats]) -> None:
    """Write deterministic LuaCov stats that upstream reporters can consume."""
    path.parent.mkdir(parents=True, exist_ok=True)
    output: list[str] = []
    for filename in sorted(stats):
        hits = stats[filename].hits
        output.append(f"{len(hits)}:{filename}")
        output.append(" ".join(str(value) for value in hits) + " ")
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


_BEGIN_MARKER = re.compile(
    r"^[ \t]*-- LUMINARI_COVERAGE_BEGIN "
    r"script=(lua-[0-9]+) offset=([0-9]+) length=([0-9]+) "
    r"sha256=([0-9a-f]{64})\r?\n",
    re.MULTILINE,
)
_END_MARKER_TEMPLATE = (
    r"^[ \t]*-- LUMINARI_COVERAGE_END script={script} sha256={digest}[ \t]*(?:\r?\n|\Z)"
)


@dataclass(frozen=True)
class DriverBlock:
    """One marked production block inside a generated lifecycle driver."""

    script_id: str
    start_offset: int
    length: int
    driver_start_line: int
    source_start_line: int
    line_count: int


def _parse_driver_blocks(
    driver_content: str,
    catalog: LuaCoverageCatalog,
) -> tuple[list[DriverBlock], dict[int, tuple[LuaScriptRecord, int]]]:
    blocks: list[DriverBlock] = []
    line_map: dict[int, tuple[LuaScriptRecord, int]] = {}
    position = 0
    begin_count = driver_content.count("LUMINARI_COVERAGE_BEGIN")
    end_count = driver_content.count("LUMINARI_COVERAGE_END")
    if begin_count != end_count:
        raise LuaCoverageError("Driver contains an unmatched coverage marker")

    while True:
        begin = _BEGIN_MARKER.search(driver_content, position)
        if begin is None:
            break
        script_id, offset_text, length_text, digest = begin.groups()
        record = catalog.by_id.get(script_id)
        if record is None:
            raise LuaCoverageError(f"Driver references unknown script ID: {script_id}")
        start_offset = int(offset_text)
        length = int(length_text)
        content_start = begin.end()
        content_end = content_start + length
        if start_offset + length > len(record.content):
            raise LuaCoverageError(f"Driver block exceeds source bounds: {script_id}")
        snippet = driver_content[content_start:content_end]
        expected = record.content[start_offset : start_offset + length]
        if snippet != expected:
            raise LuaCoverageError(f"Driver/source content mismatch: {script_id}")
        actual_digest = hashlib.sha256(snippet.encode("utf-8")).hexdigest()
        if actual_digest != digest:
            raise LuaCoverageError(f"Driver block hash mismatch: {script_id}")

        end_position = content_end
        if not snippet.endswith("\n"):
            if driver_content[end_position : end_position + 1] != "\n":
                raise LuaCoverageError(
                    f"Driver block lacks an end-marker separator: {script_id}"
                )
            end_position += 1
        end_pattern = re.compile(
            _END_MARKER_TEMPLATE.format(script=script_id, digest=digest),
            re.MULTILINE,
        )
        end = end_pattern.match(driver_content, end_position)
        if end is None:
            raise LuaCoverageError(
                f"Driver block has no matching end marker: {script_id}"
            )

        driver_start_line = driver_content.count("\n", 0, content_start) + 1
        source_start_line = record.content.count("\n", 0, start_offset) + 1
        mapped_line_count = snippet.count("\n")
        if snippet and not snippet.endswith("\n"):
            mapped_line_count += 1
        for line_offset in range(mapped_line_count):
            driver_line = driver_start_line + line_offset
            source_line = source_start_line + line_offset
            if driver_line in line_map:
                raise LuaCoverageError(
                    f"Overlapping production markers on driver line {driver_line}"
                )
            line_map[driver_line] = (record, source_line)

        blocks.append(
            DriverBlock(
                script_id=script_id,
                start_offset=start_offset,
                length=length,
                driver_start_line=driver_start_line,
                source_start_line=source_start_line,
                line_count=mapped_line_count,
            )
        )
        position = end.end()

    if len(blocks) != begin_count or "LUMINARI_COVERAGE_" in driver_content[position:]:
        raise LuaCoverageError("Driver contains an unmatched coverage marker")
    return blocks, line_map


def _resolve_driver_path(
    filename: str,
    *,
    drivers_dir: Path,
    collection_cwd: Path,
) -> Path:
    path = Path(filename)
    resolved = (
        path.resolve() if path.is_absolute() else (collection_cwd / path).resolve()
    )
    try:
        resolved.relative_to(drivers_dir.resolve())
    except ValueError as error:
        raise LuaCoverageError(
            f"LuaCov collected an unexpected non-driver path: {filename}"
        ) from error
    if not resolved.is_file():
        raise LuaCoverageError(f"LuaCov driver is missing: {filename}")
    return resolved


def map_driver_stats(
    *,
    catalog: LuaCoverageCatalog,
    raw_stats: Mapping[str, LuaCovStats],
    drivers_dir: Path,
    collection_cwd: Path,
) -> tuple[dict[str, LuaCovStats], dict[str, Any]]:
    """Map raw generated-driver hits to every stable extracted Lua source."""
    mutable_hits = {
        record.script_id: [0] * record.report_line_count for record in catalog.records
    }
    driver_summaries: list[dict[str, Any]] = []
    mapped_script_ids: set[str] = set()

    for filename in sorted(raw_stats):
        stats = raw_stats[filename]
        driver_path = _resolve_driver_path(
            filename,
            drivers_dir=drivers_dir,
            collection_cwd=collection_cwd,
        )
        content = driver_path.read_text(encoding="utf-8")
        blocks, line_map = _parse_driver_blocks(content, catalog)
        total_lines = content.count("\n") + (0 if content.endswith("\n") else 1)
        generated_hit_lines = 0
        production_hit_lines = 0

        for driver_line, hit_count in enumerate(stats.hits, start=1):
            mapping = line_map.get(driver_line)
            if mapping is None:
                if hit_count > 0:
                    generated_hit_lines += 1
                continue
            record, source_line = mapping
            if source_line > record.report_line_count:
                raise LuaCoverageError(
                    f"Mapped source line exceeds {record.lua_file}: {source_line}"
                )
            mutable_hits[record.script_id][source_line - 1] += hit_count
            mapped_script_ids.add(record.script_id)
            if hit_count > 0:
                production_hit_lines += 1

        relative_driver = driver_path.relative_to(drivers_dir.resolve()).as_posix()
        driver_summaries.append(
            {
                "driver": f"drivers/{relative_driver}",
                "line_count": total_lines,
                "production_blocks": len(blocks),
                "production_mapped_lines": len(line_map),
                "production_hit_lines": production_hit_lines,
                "generated_lines": total_lines - len(line_map),
                "generated_hit_lines": generated_hit_lines,
            }
        )

    mapped_stats = {
        record.lua_file: LuaCovStats(tuple(mutable_hits[record.script_id]))
        for record in catalog.records
    }
    mapping_report = {
        "schema_version": 1,
        "tool": "LuaCov",
        "tool_version": "0.17.0",
        "production_script_count": len(catalog.records),
        "mapped_script_count": len(mapped_script_ids),
        "driver_count": len(driver_summaries),
        "generated_category": {
            "policy": "excluded from production totals and reported separately",
            "line_count": sum(item["generated_lines"] for item in driver_summaries),
            "hit_line_count": sum(
                item["generated_hit_lines"] for item in driver_summaries
            ),
        },
        "drivers": driver_summaries,
    }
    return mapped_stats, mapping_report
