#!/usr/bin/env python3
"""
LuminariGUI Source-to-Build System

Assembles source fragments into the final LuminariGUI.xml package.

Usage:
    python build.py                 # Build the package
    python build.py --validate      # Validate only, don't write
    python build.py --watch         # Rebuild on file changes
    python build.py --extract       # REVERSE: Split XML into fragments
    python build.py --diff          # Show what would change
    python build.py --clean         # Remove generated files
    python build.py --stats         # Show line counts and fragment statistics
"""

import argparse
import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

# Optional imports
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Script directory for relative paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent


class BuildConfig:
    """Configuration loaded from build.yaml"""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = SCRIPT_DIR / "build.yaml"

        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        if not YAML_AVAILABLE:
            # Fallback: parse simple YAML manually
            self._load_simple_yaml()
            return

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.package_name = config.get('package', {}).get('name', 'LuminariGUI')
        self.version = config.get('package', {}).get('version', '2.0.4.016')

        output = config.get('output', {})
        self.output_file = output.get('file', '../LuminariGUI.xml')
        self.encoding = output.get('encoding', 'UTF-8')

        options = config.get('options', {})
        self.embed_markers = options.get('embed_markers', True)
        self.marker_format = options.get('marker_format', '<!-- SOURCE: {file} -->')
        self.validate_fragments = options.get('validate_fragments', True)
        self.validate_output = options.get('validate_output', True)
        self.strip_dev_comments = options.get('strip_dev_comments', True)

        self.triggers = config.get('triggers', [])
        self.aliases = config.get('aliases', [])
        self.scripts = config.get('scripts', [])
        self.keys = config.get('keys', [])

    def _load_simple_yaml(self):
        """Simple YAML parser fallback when PyYAML not available"""
        self.package_name = 'LuminariGUI'
        self.version = '2.0.4.016'
        self.output_file = '../LuminariGUI.xml'
        self.encoding = 'UTF-8'
        self.embed_markers = True
        self.marker_format = '<!-- SOURCE: {file} -->'
        self.validate_fragments = True
        self.validate_output = True
        self.strip_dev_comments = True

        # Parse fragments from file
        self.triggers = []
        self.aliases = []
        self.scripts = []
        self.keys = []

        current_section = None
        with open(self.config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('triggers:'):
                    current_section = 'triggers'
                elif line.startswith('aliases:'):
                    current_section = 'aliases'
                elif line.startswith('scripts:'):
                    current_section = 'scripts'
                elif line.startswith('keys:'):
                    current_section = 'keys'
                elif line.startswith('- ') and current_section:
                    path = line[2:].strip()
                    getattr(self, current_section).append(path)
                elif line.startswith('version:'):
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        self.version = match.group(1)

    def increment_version(self) -> str:
        """
        Increment the build number (last part of version).
        e.g., 2.0.4.015 -> 2.0.4.016
        Returns the new version string.
        """
        parts = self.version.split('.')
        if len(parts) >= 1:
            # Get the last part and increment it
            last_part = parts[-1]
            # Preserve leading zeros by tracking the width
            width = len(last_part)
            try:
                new_num = int(last_part) + 1
                parts[-1] = str(new_num).zfill(width)
            except ValueError:
                # If last part isn't a number, just append .1
                parts.append('1')

        self.version = '.'.join(parts)
        return self.version

    def save_version(self) -> bool:
        """
        Save the current version back to build.yaml.
        Returns True on success, False on error.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace the version line
            new_content = re.sub(
                r'(version:\s*")[^"]+(")',
                rf'\g<1>{self.version}\2',
                content
            )

            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True
        except Exception as e:
            print(f"  ERROR: Failed to save version to {self.config_path}: {e}")
            return False


class FragmentValidator:
    """Validates XML fragments for correctness"""

    @staticmethod
    def validate_fragment(content: str, filepath: str) -> tuple[bool, list[str]]:
        """
        Validate a single XML fragment.
        Returns (is_valid, list_of_errors)
        """
        errors = []

        # Wrap in a root element for parsing
        wrapped = f"<root>{content}</root>"

        try:
            ET.fromstring(wrapped)
        except ET.ParseError as e:
            errors.append(f"{filepath}: XML parse error - {e}")
            return False, errors

        return True, errors

    @staticmethod
    def validate_final_xml(content: str) -> tuple[bool, list[str]]:
        """
        Validate the final assembled XML.
        Returns (is_valid, list_of_errors)
        """
        errors = []

        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            errors.append(f"Final XML parse error: {e}")
            return False, errors

        # Check root element
        if root.tag != 'MudletPackage':
            errors.append(f"Root element should be 'MudletPackage', found '{root.tag}'")

        # Check for required packages
        required = {'TriggerPackage', 'AliasPackage', 'ScriptPackage', 'KeyPackage'}
        found = {child.tag for child in root}
        missing = required - found
        if missing:
            errors.append(f"Missing required packages: {missing}")

        return len(errors) == 0, errors


class Builder:
    """Main build class - assembles fragments into final XML"""

    def __init__(self, config: BuildConfig = None):
        self.config = config or BuildConfig()
        self.validator = FragmentValidator()

    def get_output_path(self) -> Path:
        """Get absolute path to output file"""
        output_path = Path(self.config.output_file)
        if not output_path.is_absolute():
            output_path = SCRIPT_DIR / output_path
        return output_path.resolve()

    def get_archive_dir(self) -> Path:
        """Get absolute path to archive directory"""
        return PROJECT_ROOT / "docs" / "archive"

    def get_existing_version(self, xml_path: Path) -> str | None:
        """Extract version number from existing XML file"""
        if not xml_path.exists():
            return None

        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                # Read first few lines to find version
                for _ in range(10):
                    line = f.readline()
                    match = re.search(r'<MudletPackage\s+version="([^"]+)"', line)
                    if match:
                        return match.group(1)
        except Exception as e:
            print(f"  WARNING: Could not read version from {xml_path}: {e}")

        return None

    def archive_existing(self) -> bool:
        """
        Archive the existing LuminariGUI.xml before building a new one.
        Renames to LuminariGUI.xml_<version> and moves to docs/archive/
        Returns True if archived (or no file to archive), False on error.
        """
        output_path = self.get_output_path()

        if not output_path.exists():
            print("  No existing file to archive.")
            return True

        # Get version from existing file
        version = self.get_existing_version(output_path)
        if not version:
            print("  WARNING: Could not determine version of existing file, skipping archive.")
            return True

        # Prepare archive destination
        archive_dir = self.get_archive_dir()
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_name = f"{output_path.name}_{version}"
        archive_path = archive_dir / archive_name

        # Check if archive already exists
        if archive_path.exists():
            print(f"  Archive {archive_name} already exists, skipping archive.")
            return True

        # Move the file
        try:
            shutil.move(str(output_path), str(archive_path))
            print(f"  Archived: {output_path.name} -> docs/archive/{archive_name}")
            return True
        except Exception as e:
            print(f"  ERROR: Failed to archive existing file: {e}")
            return False

    def read_skeleton(self) -> str:
        """Read skeleton.xml template"""
        skeleton_path = SCRIPT_DIR / "skeleton.xml"
        with open(skeleton_path, 'r', encoding='utf-8') as f:
            return f.read()

    def read_fragment(self, rel_path: str) -> str:
        """Read a single fragment file"""
        fragment_path = SCRIPT_DIR / rel_path
        with open(fragment_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Strip dev comments if configured
        if self.config.strip_dev_comments:
            content = re.sub(r'<!--\s*DEV:.*?-->\n?', '', content, flags=re.DOTALL)

        return content

    def assemble_fragments(self, fragment_list: list[str], indent: str = "\t\t\t") -> str:
        """
        Assemble multiple fragments into a single block.
        Returns the combined content with optional source markers.
        """
        parts = []

        for rel_path in fragment_list:
            try:
                content = self.read_fragment(rel_path)
            except FileNotFoundError:
                print(f"  WARNING: Fragment not found: {rel_path}")
                continue

            # Validate fragment if configured
            if self.config.validate_fragments:
                is_valid, errors = self.validator.validate_fragment(content, rel_path)
                if not is_valid:
                    for err in errors:
                        print(f"  ERROR: {err}")
                    continue

            # Add source markers if configured
            if self.config.embed_markers:
                marker = self.config.marker_format.format(file=rel_path)
                border = "<!-- " + "=" * 60 + " -->"
                parts.append(f"{indent}{border}")
                parts.append(f"{indent}{marker}")
                parts.append(f"{indent}{border}")

            # Add the fragment content (already indented properly from extraction)
            parts.append(content.rstrip())

            if self.config.embed_markers:
                end_marker = f"<!-- END: {rel_path} -->"
                parts.append(f"{indent}{border}")
                parts.append(f"{indent}{end_marker}")
                parts.append(f"{indent}{border}")

        return "\n".join(parts)

    def build(self, validate_only: bool = False) -> tuple[bool, str]:
        """
        Build the final XML from fragments.
        Returns (success, output_content)
        """
        # Increment version before building (skip for validate-only)
        if not validate_only:
            old_version = self.config.version
            new_version = self.config.increment_version()
            print(f"Incrementing version: {old_version} -> {new_version}")
            if not self.config.save_version():
                print("  WARNING: Failed to save version to build.yaml")

        print(f"Building {self.config.package_name} v{self.config.version}...")

        # Read skeleton
        try:
            skeleton = self.read_skeleton()
        except FileNotFoundError:
            print("ERROR: skeleton.xml not found")
            return False, ""

        # Assemble each section
        print("  Assembling triggers...")
        triggers_content = self.assemble_fragments(self.config.triggers)

        print("  Assembling aliases...")
        aliases_content = self.assemble_fragments(self.config.aliases)

        print("  Assembling scripts...")
        scripts_content = self.assemble_fragments(self.config.scripts)

        print("  Assembling keys...")
        keys_content = self.assemble_fragments(self.config.keys)

        # Replace placeholders
        output = skeleton
        output = output.replace("{{VERSION}}", self.config.version)
        output = output.replace("{{TRIGGERS}}", triggers_content)
        output = output.replace("{{ALIASES}}", aliases_content)
        output = output.replace("{{SCRIPTS}}", scripts_content)
        output = output.replace("{{KEYS}}", keys_content)

        # Validate final output
        if self.config.validate_output:
            print("  Validating output...")
            is_valid, errors = self.validator.validate_final_xml(output)
            if not is_valid:
                for err in errors:
                    print(f"  ERROR: {err}")
                return False, output

        if validate_only:
            print("  Validation passed (dry run, no file written)")
            return True, output

        # Archive existing file before overwriting
        print("  Archiving existing file...")
        if not self.archive_existing():
            print("  WARNING: Archive failed, continuing with build anyway.")

        # Write output
        output_path = self.get_output_path()
        print(f"  Writing to {output_path}...")
        with open(output_path, 'w', encoding=self.config.encoding) as f:
            f.write(output)

        line_count = output.count('\n') + 1
        print(f"  Done! {line_count} lines written.")
        return True, output

    def diff(self) -> bool:
        """Show differences between current output and what build would produce"""
        success, new_content = self.build(validate_only=True)
        if not success:
            return False

        output_path = self.get_output_path()
        if not output_path.exists():
            print(f"Output file {output_path} does not exist. Build would create it.")
            return True

        with open(output_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        if current_content == new_content:
            print("No changes - output is up to date.")
            return True

        # Simple line-by-line diff
        current_lines = current_content.splitlines()
        new_lines = new_content.splitlines()

        import difflib
        diff = difflib.unified_diff(
            current_lines, new_lines,
            fromfile='current', tofile='new',
            lineterm=''
        )

        diff_output = '\n'.join(diff)
        if diff_output:
            print("Changes detected:")
            print(diff_output[:5000])  # Limit output
            if len(diff_output) > 5000:
                print(f"... (truncated, {len(diff_output)} total characters)")

        return True

    def stats(self) -> None:
        """Show statistics about fragments and output"""
        print(f"Build Statistics for {self.config.package_name}")
        print("=" * 50)

        total_lines = 0
        sections = [
            ("Triggers", self.config.triggers),
            ("Aliases", self.config.aliases),
            ("Scripts", self.config.scripts),
            ("Keys", self.config.keys),
        ]

        for section_name, fragments in sections:
            section_lines = 0
            print(f"\n{section_name}:")
            for rel_path in fragments:
                try:
                    content = self.read_fragment(rel_path)
                    lines = content.count('\n') + 1
                    section_lines += lines
                    print(f"  {rel_path}: {lines} lines")
                except FileNotFoundError:
                    print(f"  {rel_path}: NOT FOUND")
            print(f"  Subtotal: {section_lines} lines")
            total_lines += section_lines

        print(f"\n{'=' * 50}")
        print(f"Total source lines: {total_lines}")

        # Check output file
        output_path = self.get_output_path()
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                output_lines = f.read().count('\n') + 1
            print(f"Output file lines: {output_lines}")

    def clean(self) -> None:
        """Remove generated output file"""
        output_path = self.get_output_path()
        if output_path.exists():
            output_path.unlink()
            print(f"Removed {output_path}")
        else:
            print(f"Nothing to clean - {output_path} does not exist")


class Extractor:
    """Extracts fragments from existing monolithic XML using raw text parsing"""

    def __init__(self, config: BuildConfig = None):
        self.config = config or BuildConfig()
        self.lines = []
        self.generated_files = []

    def get_input_path(self) -> Path:
        """Get path to existing XML file"""
        output_path = Path(self.config.output_file)
        if not output_path.is_absolute():
            output_path = SCRIPT_DIR / output_path
        return output_path.resolve()

    def extract(self) -> bool:
        """
        Extract fragments from existing LuminariGUI.xml
        Uses raw text parsing to preserve original formatting
        """
        input_path = self.get_input_path()

        if not input_path.exists():
            print(f"ERROR: Input file not found: {input_path}")
            return False

        print(f"Extracting fragments from {input_path}...")

        with open(input_path, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()

        # Find version
        for line in self.lines[:10]:
            match = re.search(r'version="([^"]+)"', line)
            if match:
                print(f"  Package version: {match.group(1)}")
                break

        # Find package boundaries
        boundaries = self._find_package_boundaries()

        # Extract each section
        self._extract_section('triggers', boundaries.get('TriggerPackage', (0, 0)))
        self._extract_section('aliases', boundaries.get('AliasPackage', (0, 0)))
        self._extract_section('scripts', boundaries.get('ScriptPackage', (0, 0)))
        self._extract_section('keys', boundaries.get('KeyPackage', (0, 0)))

        # Generate build.yaml with actual file list
        self._generate_build_yaml()

        print("\nExtraction complete!")
        print("Review the generated files in src/ and adjust build.yaml as needed.")
        return True

    def _find_package_boundaries(self) -> dict:
        """Find start/end line numbers for each package"""
        boundaries = {}
        package_names = ['TriggerPackage', 'AliasPackage', 'ScriptPackage', 'KeyPackage']

        for pkg in package_names:
            start = None
            end = None
            for i, line in enumerate(self.lines):
                if f'<{pkg}>' in line or f'<{pkg} ' in line:
                    start = i
                elif f'</{pkg}>' in line:
                    end = i
                    break
            if start is not None and end is not None:
                boundaries[pkg] = (start, end)

        return boundaries

    def _extract_section(self, section_name: str, boundaries: tuple):
        """Extract fragments from a section"""
        start, end = boundaries
        if start == 0 and end == 0:
            print(f"  No {section_name} section found")
            return

        section_lines = self.lines[start:end+1]
        content = ''.join(section_lines)

        if section_name == 'triggers':
            self._extract_triggers(content, start)
        elif section_name == 'aliases':
            self._extract_aliases(content, start)
        elif section_name == 'scripts':
            self._extract_scripts(content, start)
        elif section_name == 'keys':
            self._extract_keys(content, start)

    def _write_fragment(self, rel_path: str, content: str):
        """Write a fragment file"""
        fragment_path = SCRIPT_DIR / rel_path
        fragment_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure content ends with newline
        if not content.endswith('\n'):
            content += '\n'

        with open(fragment_path, 'w', encoding='utf-8') as f:
            f.write(content)

        lines = content.count('\n')
        print(f"  Wrote {rel_path} ({lines} lines)")
        self.generated_files.append(rel_path)

    def _find_element_bounds(self, lines: list, tag: str, start_idx: int = 0, target_depth: int = 0) -> list:
        """
        Find all occurrences of an element in lines at a specific depth.
        Returns list of (start_line, end_line, name) tuples.

        Args:
            lines: List of lines to search
            tag: Element tag name to find
            start_idx: Starting line index
            target_depth: Capture elements when depth equals this value (after incrementing)
                         0 = top-level elements, 1 = elements nested 1 level deep, etc.
        """
        results = []
        i = start_idx
        depth = 0
        current_start = None
        current_name = None
        capture_depth = None

        while i < len(lines):
            line = lines[i]

            # Check for opening tag
            open_match = re.search(rf'<{tag}\s+[^>]*>', line)
            if open_match:
                depth += 1
                # Check AFTER incrementing depth
                if capture_depth is None and depth == target_depth + 1:
                    # Start capturing
                    current_start = i
                    capture_depth = depth
                    # Try to find name on next lines
                    for j in range(i, min(i+5, len(lines))):
                        name_match = re.search(r'<name>([^<]+)</name>', lines[j])
                        if name_match:
                            current_name = name_match.group(1)
                            break

            # Check for closing tag
            if f'</{tag}>' in line:
                if capture_depth is not None and depth == capture_depth:
                    results.append((current_start, i, current_name or f"{tag}_{len(results)}"))
                    current_start = None
                    current_name = None
                    capture_depth = None
                depth -= 1

            i += 1

        return results

    def _find_direct_children(self, lines: list, parent_tag: str, child_tag: str) -> list:
        """
        Find direct children of a parent element.
        First finds the parent, then finds children at depth=1 within parent.
        """
        # Find the parent element
        parent_bounds = self._find_element_bounds(lines, parent_tag, target_depth=0)
        if not parent_bounds:
            return []

        # Get the first parent (main group)
        parent_start, parent_end, _ = parent_bounds[0]

        # Now find children within the parent
        parent_lines = lines[parent_start:parent_end+1]

        # Find all child elements - track depth based on the tag type
        results = []
        depth = 0
        current_start = None
        current_name = None

        # When parent_tag == child_tag, the parent itself is counted at depth 1
        # So direct children are at depth 2
        # When parent_tag != child_tag, direct children are at depth 1
        target_depth = 2 if (parent_tag == child_tag) else 1

        for i, line in enumerate(parent_lines):
            # Check for opening tag of our target element
            open_match = re.search(rf'<{child_tag}\s+[^>]*>', line)

            if open_match:
                depth += 1
                if depth == target_depth:
                    current_start = i
                    # Try to find name
                    for j in range(i, min(i+5, len(parent_lines))):
                        name_match = re.search(r'<name>([^<]+)</name>', parent_lines[j])
                        if name_match:
                            current_name = name_match.group(1)
                            break

            # Check for closing tag
            if f'</{child_tag}>' in line:
                if depth == target_depth and current_start is not None:
                    results.append((
                        parent_start + current_start,
                        parent_start + i,
                        current_name or f"{child_tag}_{len(results)}"
                    ))
                    current_start = None
                    current_name = None
                depth -= 1

        return results

    def _extract_triggers(self, content: str, base_line: int):
        """Extract trigger fragments"""
        lines = content.split('\n')
        fragments = []

        # Find direct TriggerGroup children of the main TriggerGroup
        children = self._find_direct_children(lines, 'TriggerGroup', 'TriggerGroup')

        for start, end, name in children:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            fragment_lines = lines[start:end+1]
            fragment_content = '\n'.join(fragment_lines)

            rel_path = f"src/triggers/{len(fragments):02d}_{safe_name}.xml"
            self._write_fragment(rel_path, fragment_content)
            fragments.append(rel_path)

        print(f"  Extracted {len(fragments)} trigger fragments")

    def _extract_aliases(self, content: str, base_line: int):
        """Extract alias fragments"""
        lines = content.split('\n')
        fragments = []

        # Find direct AliasGroup children of the main AliasGroup
        children = self._find_direct_children(lines, 'AliasGroup', 'AliasGroup')

        for start, end, name in children:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            fragment_lines = lines[start:end+1]
            fragment_content = '\n'.join(fragment_lines)

            rel_path = f"src/aliases/{len(fragments):02d}_{safe_name}.xml"
            self._write_fragment(rel_path, fragment_content)
            fragments.append(rel_path)

        print(f"  Extracted {len(fragments)} alias fragments")

    def _extract_scripts(self, content: str, base_line: int):
        """Extract script fragments - preserving structural groups for proper assembly"""
        lines = content.split('\n')
        fragments = []

        # Find direct ScriptGroup children of the main ScriptGroup
        children = self._find_direct_children(lines, 'ScriptGroup', 'ScriptGroup')

        for start, end, name in children:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            fragment_lines = lines[start:end+1]
            fragment_content = '\n'.join(fragment_lines)

            # Keep each major ScriptGroup as a complete fragment
            # This preserves the nested structure for proper assembly
            rel_path = f"src/scripts/{len(fragments):02d}_{safe_name}.xml"
            self._write_fragment(rel_path, fragment_content)
            fragments.append(rel_path)

        print(f"  Extracted {len(fragments)} script fragments")

    def _extract_gui_subscripts(self, content: str, fragments: list):
        """Extract individual scripts from the GUI ScriptGroup"""
        lines = content.split('\n')
        gui_idx = 0

        # Find direct children of the GUI group - these are CSSman, GUI (inner)
        children = self._find_direct_children(lines, 'ScriptGroup', 'ScriptGroup')

        for start, end, name in children:
            fragment_lines = lines[start:end+1]
            fragment_content = '\n'.join(fragment_lines)

            if name == "CSSman":
                rel_path = f"src/scripts/gui/{gui_idx:02d}_cssman.xml"
                self._write_fragment(rel_path, fragment_content)
                fragments.append(rel_path)
                gui_idx += 1
            elif name == "GUI":
                # Extract individual scripts from inner GUI group
                inner_lines = fragment_lines
                scripts = self._find_element_bounds(inner_lines, 'Script', target_depth=0)

                for s_start, s_end, s_name in scripts:
                    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', s_name.lower().replace(' ', '_').replace('/', '_'))
                    script_lines = inner_lines[s_start:s_end+1]
                    script_content = '\n'.join(script_lines)

                    rel_path = f"src/scripts/gui/{gui_idx:02d}_{safe_name}.xml"
                    self._write_fragment(rel_path, script_content)
                    fragments.append(rel_path)
                    gui_idx += 1

    def _extract_yatco_subscripts(self, content: str, fragments: list):
        """Extract individual scripts from the YATCO ScriptGroup"""
        lines = content.split('\n')
        yatco_idx = 0

        # Find all Scripts at any depth in YATCO
        scripts = self._find_all_scripts(lines)

        for start, end, name in scripts:
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
            fragment_lines = lines[start:end+1]
            fragment_content = '\n'.join(fragment_lines)

            rel_path = f"src/scripts/yatco/{yatco_idx:02d}_{safe_name}.xml"
            self._write_fragment(rel_path, fragment_content)
            fragments.append(rel_path)
            yatco_idx += 1

    def _find_all_scripts(self, lines: list) -> list:
        """Find all Script elements regardless of depth"""
        results = []
        depth = 0
        current_start = None
        current_name = None

        for i, line in enumerate(lines):
            # Check for Script opening tag
            if '<Script ' in line:
                if depth == 0:
                    current_start = i
                    # Find name
                    for j in range(i, min(i+5, len(lines))):
                        name_match = re.search(r'<name>([^<]+)</name>', lines[j])
                        if name_match:
                            current_name = name_match.group(1)
                            break
                depth += 1

            # Check for Script closing tag
            if '</Script>' in line:
                depth -= 1
                if depth == 0 and current_start is not None:
                    results.append((current_start, i, current_name or f"script_{len(results)}"))
                    current_start = None
                    current_name = None

        return results

    def _extract_keys(self, content: str, base_line: int):
        """Extract key fragments"""
        lines = content.split('\n')

        # Find all Key elements
        keys = self._find_element_bounds(lines, 'Key')

        if keys:
            # Combine all keys into single fragment
            key_lines = []
            for start, end, name in keys:
                key_lines.extend(lines[start:end+1])

            fragment_content = '\n'.join(key_lines)
            rel_path = "src/keys/00_movement.xml"
            self._write_fragment(rel_path, fragment_content)

            print(f"  Extracted {len(keys)} key bindings to 1 fragment")

    def _generate_build_yaml(self):
        """Generate build.yaml with the list of extracted files"""
        # Categorize files
        triggers = sorted([f for f in self.generated_files if f.startswith('src/triggers/')])
        aliases = sorted([f for f in self.generated_files if f.startswith('src/aliases/')])
        scripts = sorted([f for f in self.generated_files if f.startswith('src/scripts/') and '/gui/' not in f and '/yatco/' not in f])
        gui_scripts = sorted([f for f in self.generated_files if '/gui/' in f])
        yatco_scripts = sorted([f for f in self.generated_files if '/yatco/' in f])
        keys = sorted([f for f in self.generated_files if f.startswith('src/keys/')])

        # Build scripts list in correct order
        all_scripts = []
        for s in scripts:
            if 'msdpmapper' in s.lower():
                all_scripts.insert(0, s)  # MSDPMapper first
            elif 'yatcoconfig' in s.lower():
                pass  # Will add after GUI scripts
            else:
                all_scripts.append(s)

        all_scripts.extend(gui_scripts)

        # Add YATCOConfig after GUI
        for s in scripts:
            if 'yatcoconfig' in s.lower():
                all_scripts.append(s)

        all_scripts.extend(yatco_scripts)

        yaml_content = f'''# theGUI/build.yaml
# LuminariGUI Source-to-Build Configuration
# AUTO-GENERATED by build.py --extract

package:
  name: "LuminariGUI"
  version: "2.0.4.015"

output:
  file: "../LuminariGUI.xml"
  encoding: "UTF-8"

options:
  embed_markers: false
  marker_format: "<!-- SOURCE: {{file}} -->"
  validate_fragments: true
  validate_output: true
  strip_dev_comments: true

triggers:
'''
        for f in triggers:
            yaml_content += f'  - {f}\n'

        yaml_content += '\naliases:\n'
        for f in aliases:
            yaml_content += f'  - {f}\n'

        yaml_content += '\nscripts:\n'
        for f in all_scripts:
            yaml_content += f'  - {f}\n'

        yaml_content += '\nkeys:\n'
        for f in keys:
            yaml_content += f'  - {f}\n'

        yaml_path = SCRIPT_DIR / 'build.yaml'
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        print(f"  Updated build.yaml with {len(self.generated_files)} fragments")


class Watcher:
    """Watch for file changes and rebuild"""

    def __init__(self, builder: Builder):
        self.builder = builder
        self.config = builder.config

    def watch(self):
        """Watch source files and rebuild on changes"""
        print("Watching for changes... (Ctrl+C to stop)")

        src_dir = SCRIPT_DIR / "src"
        last_build = 0

        try:
            while True:
                # Get latest modification time of any source file
                latest_mtime = 0
                for path in src_dir.rglob("*.xml"):
                    mtime = path.stat().st_mtime
                    if mtime > latest_mtime:
                        latest_mtime = mtime

                # Also check skeleton and build.yaml
                for config_file in [SCRIPT_DIR / "skeleton.xml", SCRIPT_DIR / "build.yaml"]:
                    if config_file.exists():
                        mtime = config_file.stat().st_mtime
                        if mtime > latest_mtime:
                            latest_mtime = mtime

                # Rebuild if changed
                if latest_mtime > last_build:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"\n[{timestamp}] Change detected, rebuilding...")
                    self.builder.build()
                    last_build = time.time()

                time.sleep(1)

        except KeyboardInterrupt:
            print("\nStopped watching.")


def main():
    parser = argparse.ArgumentParser(
        description="LuminariGUI Source-to-Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python build.py                 Build the package
    python build.py --validate      Validate only, don't write
    python build.py --extract       Split existing XML into fragments
    python build.py --diff          Show what would change
    python build.py --stats         Show fragment statistics
        """
    )

    parser.add_argument('--validate', action='store_true',
                        help='Validate fragments and output, but do not write')
    parser.add_argument('--extract', action='store_true',
                        help='Extract fragments from existing LuminariGUI.xml')
    parser.add_argument('--diff', action='store_true',
                        help='Show differences between current output and what build would produce')
    parser.add_argument('--watch', action='store_true',
                        help='Watch source files and rebuild on changes')
    parser.add_argument('--clean', action='store_true',
                        help='Remove generated output file')
    parser.add_argument('--stats', action='store_true',
                        help='Show line counts and fragment statistics')
    parser.add_argument('--fail-on-diff', action='store_true',
                        help='Exit with error if output differs (for CI)')

    args = parser.parse_args()

    # Load configuration
    config = BuildConfig()

    if args.extract:
        extractor = Extractor(config)
        success = extractor.extract()
        sys.exit(0 if success else 1)

    builder = Builder(config)

    if args.clean:
        builder.clean()
        sys.exit(0)

    if args.stats:
        builder.stats()
        sys.exit(0)

    if args.diff:
        success = builder.diff()
        if args.fail_on_diff:
            # Check if there are differences
            _, new_content = builder.build(validate_only=True)
            output_path = builder.get_output_path()
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as f:
                    current = f.read()
                if current != new_content:
                    print("ERROR: Output differs from source. Run 'python build.py' to rebuild.")
                    sys.exit(1)
        sys.exit(0 if success else 1)

    if args.watch:
        watcher = Watcher(builder)
        watcher.watch()
        sys.exit(0)

    # Default: build
    success, _ = builder.build(validate_only=args.validate)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
