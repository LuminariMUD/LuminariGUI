#!/usr/bin/env python3
"""Map a generated LuminariGUI.xml line to its physical source fragment."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from theGUI.build import (  # noqa: E402
    BuildConfig,
    Builder,
    FragmentBuildError,
    ResolvedFragmentLine,
)

SECTION_NAMES = ("triggers", "aliases", "scripts", "keys")


class GeneratedLineMappingError(RuntimeError):
    """Raised when the generated package cannot be mapped safely."""


@dataclass(frozen=True)
class GeneratedLineLocation:
    """One generated XML line and its physical source location."""

    generated_file: str
    generated_line: int
    generated_text: str
    source_fragment: str | None
    source_line: int | None
    section: str | None
    entry_fragment: str | None
    kind: str

    def as_dict(self) -> dict[str, str | int | None]:
        """Return a stable JSON-safe representation."""
        return asdict(self)


@dataclass(frozen=True)
class _BuildLine:
    text: str
    source_fragment: str | None
    source_line: int | None
    section: str | None
    entry_fragment: str | None
    kind: str


class GeneratedXmlLineMapper:
    """Reconstruct the canonical build with exact line provenance."""

    def __init__(
        self,
        project_root: Path = PROJECT_ROOT,
        *,
        config_path: Path | None = None,
        xml_path: Path | None = None,
    ):
        self.project_root = project_root.resolve()
        self.config_path = (
            config_path or self.project_root / "theGUI/build.yaml"
        ).resolve()
        self.config = BuildConfig(self.config_path)
        self.builder = Builder(self.config)
        self.xml_path = (xml_path or self.builder.get_output_path()).resolve()
        self._lines = self._build_map()

    @property
    def line_count(self) -> int:
        """Return the number of generated XML lines available for mapping."""
        return len(self._lines)

    def map_line(self, line_number: int) -> GeneratedLineLocation:
        """Return the exact physical origin for a one-based generated line."""
        if not 1 <= line_number <= self.line_count:
            raise GeneratedLineMappingError(
                f"line must be between 1 and {self.line_count}, got {line_number}"
            )

        record = self._lines[line_number - 1]
        return GeneratedLineLocation(
            generated_file=self._relative(self.xml_path),
            generated_line=line_number,
            generated_text=record.text.rstrip("\r\n"),
            source_fragment=record.source_fragment,
            source_line=record.source_line,
            section=record.section,
            entry_fragment=record.entry_fragment,
            kind=record.kind,
        )

    def _relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.project_root).as_posix()
        except ValueError:
            return str(path.resolve())

    @staticmethod
    def _trim_lines(
        lines: list[ResolvedFragmentLine], target_length: int
    ) -> list[ResolvedFragmentLine]:
        result: list[ResolvedFragmentLine] = []
        remaining = target_length
        for line in lines:
            if remaining == 0:
                break
            text = line.text[:remaining]
            if text:
                result.append(replace(line, text=text))
                remaining -= len(text)
        if remaining:
            raise GeneratedLineMappingError(
                "internal fragment map ended before assembled content"
            )
        return result

    @staticmethod
    def _join_parts(parts: list[list[_BuildLine]]) -> list[_BuildLine]:
        result: list[_BuildLine] = []
        for index, part in enumerate(parts):
            if index:
                if result:
                    result[-1] = replace(result[-1], text=result[-1].text + "\n")
                else:
                    result.append(_BuildLine("\n", None, None, None, None, "generated"))
            result.extend(part)
        return result

    def _generated_part(
        self,
        text: str,
        *,
        section: str,
        entry_fragment: str,
    ) -> list[_BuildLine]:
        return [
            _BuildLine(
                text=text,
                source_fragment=None,
                source_line=None,
                section=section,
                entry_fragment=entry_fragment,
                kind="generated-marker",
            )
        ]

    def _assemble_section(self, section: str) -> list[_BuildLine]:
        entries: list[str] = getattr(self.config, section)
        parts: list[list[_BuildLine]] = []
        indent = "\t\t\t"
        border = "<!-- " + "=" * 60 + " -->"

        for entry in entries:
            entry_path = (self.config_path.parent / entry).resolve()
            entry_fragment = self._relative(entry_path)
            content, resolved_lines = (
                self.builder.fragment_resolver.resolve_with_line_map(entry_path)
            )
            trimmed = content.rstrip()
            physical_lines = self._trim_lines(resolved_lines, len(trimmed))
            fragment_part = [
                _BuildLine(
                    text=line.text,
                    source_fragment=self._relative(
                        self.config_path.parent / line.source_fragment
                    ),
                    source_line=line.source_line,
                    section=section,
                    entry_fragment=entry_fragment,
                    kind="fragment",
                )
                for line in physical_lines
            ]

            if self.config.embed_markers:
                marker = self.config.marker_format.format(file=entry)
                parts.extend(
                    [
                        self._generated_part(
                            f"{indent}{border}",
                            section=section,
                            entry_fragment=entry_fragment,
                        ),
                        self._generated_part(
                            f"{indent}{marker}",
                            section=section,
                            entry_fragment=entry_fragment,
                        ),
                        self._generated_part(
                            f"{indent}{border}",
                            section=section,
                            entry_fragment=entry_fragment,
                        ),
                    ]
                )

            parts.append(fragment_part)

            if self.config.embed_markers:
                parts.extend(
                    [
                        self._generated_part(
                            f"{indent}{border}",
                            section=section,
                            entry_fragment=entry_fragment,
                        ),
                        self._generated_part(
                            f"{indent}<!-- END: {entry} -->",
                            section=section,
                            entry_fragment=entry_fragment,
                        ),
                        self._generated_part(
                            f"{indent}{border}",
                            section=section,
                            entry_fragment=entry_fragment,
                        ),
                    ]
                )

        return self._join_parts(parts)

    def _map_skeleton(self) -> list[_BuildLine]:
        skeleton_path = self.builder.script_dir / "skeleton.xml"
        skeleton = self.builder.read_skeleton()
        assembled = {
            section: self._assemble_section(section) for section in SECTION_NAMES
        }
        placeholders = {
            "{{TRIGGERS}}": "triggers",
            "{{ALIASES}}": "aliases",
            "{{SCRIPTS}}": "scripts",
            "{{KEYS}}": "keys",
        }
        output: list[_BuildLine] = []

        for source_line, text in enumerate(skeleton.splitlines(keepends=True), start=1):
            matches = [token for token in placeholders if token in text]
            if not matches:
                output.append(
                    _BuildLine(
                        text=text.replace("{{VERSION}}", self.config.version),
                        source_fragment=self._relative(skeleton_path),
                        source_line=source_line,
                        section=None,
                        entry_fragment=None,
                        kind="skeleton",
                    )
                )
                continue

            if len(matches) != 1:
                raise GeneratedLineMappingError(
                    f"multiple build placeholders share skeleton line {source_line}"
                )
            token = matches[0]
            prefix, suffix = text.split(token, maxsplit=1)
            if prefix or suffix not in ("", "\n"):
                raise GeneratedLineMappingError(
                    f"{token} must occupy its own skeleton line for exact mapping"
                )

            section_lines = list(assembled[placeholders[token]])
            if section_lines:
                section_lines[-1] = replace(
                    section_lines[-1], text=section_lines[-1].text + suffix
                )
                output.extend(section_lines)
            else:
                output.append(
                    _BuildLine(
                        text=suffix,
                        source_fragment=self._relative(skeleton_path),
                        source_line=source_line,
                        section=None,
                        entry_fragment=None,
                        kind="skeleton",
                    )
                )

        return output

    def _build_map(self) -> list[_BuildLine]:
        try:
            mapped_lines = self._map_skeleton()
            with contextlib.redirect_stdout(io.StringIO()):
                success, expected = self.builder.build(validate_only=True)
        except (FragmentBuildError, OSError) as error:
            raise GeneratedLineMappingError(str(error)) from error

        if not success:
            raise GeneratedLineMappingError("the canonical in-memory build is invalid")
        mapped_content = "".join(line.text for line in mapped_lines)
        if mapped_content != expected:
            raise GeneratedLineMappingError(
                "internal source map differs from canonical builder output"
            )
        if not self.xml_path.is_file():
            raise GeneratedLineMappingError(f"generated XML not found: {self.xml_path}")
        try:
            actual = self.xml_path.read_text(encoding=self.config.encoding)
        except UnicodeDecodeError as error:
            raise GeneratedLineMappingError(
                f"generated XML is not valid {self.config.encoding}: {self.xml_path}"
            ) from error
        if actual != expected:
            raise GeneratedLineMappingError(
                "generated XML is stale or does not match this build manifest; "
                "run `python3 theGUI/build.py --diff`"
            )
        return mapped_lines


def _line_number(value: str) -> int:
    try:
        line = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("line must be an integer") from error
    if line < 1:
        raise argparse.ArgumentTypeError("line must be at least 1")
    return line


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("line", type=_line_number, help="one-based generated XML line")
    parser.add_argument(
        "--xml",
        type=Path,
        help="generated XML to verify and map (default: build.yaml output)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="build manifest (default: theGUI/build.yaml)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser


def format_location(location: GeneratedLineLocation) -> str:
    """Format one mapping for terminal diagnostics."""
    generated = f"{location.generated_file}:{location.generated_line}"
    if location.source_fragment is None or location.source_line is None:
        source = location.kind
    else:
        source = f"{location.source_fragment}:{location.source_line}"
    context = ""
    if location.section and location.entry_fragment:
        context = f" ({location.section}; entry {location.entry_fragment})"
    return f"{generated} -> {source}{context}"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        mapper = GeneratedXmlLineMapper(
            PROJECT_ROOT,
            config_path=args.config,
            xml_path=args.xml,
        )
        location = mapper.map_line(args.line)
    except GeneratedLineMappingError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(location.as_dict(), indent=2, sort_keys=True))
    else:
        print(format_location(location))
    return 0


if __name__ == "__main__":
    sys.exit(main())
