#!/usr/bin/env python3
"""
LuminariGUI Package Manager

Creates distributable .mpackage files for Mudlet with full release workflow support.

This script integrates with build.py and uses build.yaml for version management.

Usage:
    python package.py create              # Create a local distributable package
    python package.py create --dev        # Create dev package with timestamp
    python package.py release             # Build and publish a release
    python package.py list                # List existing packages
    python package.py clean               # Clean old dev packages

Examples:
    python package.py create                    # Build XML, create package
    python package.py create --skip-build       # Package existing XML
    python package.py create --skip-tests       # Skip test suite
    python package.py release --dry-run         # Preview publication
    python package.py release                   # Publish refs and GitHub assets
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Script directory for relative paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

VERSION_PATTERN = re.compile(r"^[0-9A-Za-z]+(?:[._+-][0-9A-Za-z]+)*$")
PACKAGE_ICON_NAME = "LuminariGUI.png"
PACKAGE_ICON_PATH = PROJECT_ROOT / "images" / PACKAGE_ICON_NAME


def parse_version_argument(value: str) -> str:
    """Validate a version before using it in filenames, YAML, or XML."""
    if not VERSION_PATTERN.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "version must contain only letters, numbers, '.', '_', '+', or '-'"
        )
    return value


def increment_build_version(version: str) -> str:
    """Return the version produced by build.py's normal auto-increment."""
    parts = version.split(".")
    last_part = parts[-1]
    width = len(last_part)
    try:
        parts[-1] = str(int(last_part) + 1).zfill(width)
    except ValueError:
        parts.append("1")
    return ".".join(parts)


def get_version_from_xml(xml_path: Path) -> str | None:
    """Read the embedded Mudlet package version from a built XML file."""
    try:
        return ET.parse(xml_path).getroot().attrib.get("version")
    except (ET.ParseError, OSError):
        return None


@dataclass
class PackageMetadata:
    """Metadata for a package release"""

    version: str
    package_type: str  # "release" or "development"
    created: str
    package_file: str
    file_size: int
    sha256: str
    # Minimum Mudlet this package is developed and validated against.
    # 4.21 is the floor because: Qt6 is universal from 4.20 (the stylesheets
    # are tuned for QSS under Qt6), and 4.21 fixed the resetProfile() label
    # regression that affects labels inside Adjustable/Geyser containers
    # (Mudlet #9254 / #9255). See docs/MUDLET_COMPATIBILITY.md.
    mudlet_version: str = "4.21+"
    description: str = "LuminariGUI package for LuminariMUD"

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "type": self.package_type,
            "created": self.created,
            "package_file": self.package_file,
            "file_size": self.file_size,
            "sha256": self.sha256,
            "mudlet_version": self.mudlet_version,
            "description": self.description,
        }


@dataclass
class GitStatus:
    """Git repository status"""

    is_clean: bool
    current_branch: str
    uncommitted_files: list = field(default_factory=list)
    error: str | None = None


class GitManager:
    """Manages git operations for release workflow"""

    @staticmethod
    def run(command: list, check: bool = True) -> tuple[str, str, int]:
        """Run a git command and return (stdout, stderr, returncode)"""
        try:
            result = subprocess.run(
                ["git"] + command,
                capture_output=True,
                text=True,
                check=check,
                cwd=PROJECT_ROOT,
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.CalledProcessError as e:
            return (
                e.stdout.strip() if e.stdout else "",
                e.stderr.strip() if e.stderr else "",
                e.returncode,
            )
        except FileNotFoundError:
            return "", "Git not found", 1

    def get_status(self) -> GitStatus:
        """Get current git repository status"""
        stdout, stderr, rc = self.run(["branch", "--show-current"])
        if rc != 0:
            return GitStatus(is_clean=False, current_branch="", error=stderr)

        current_branch = stdout

        stdout, stderr, rc = self.run(["status", "--porcelain"])
        if rc != 0:
            return GitStatus(
                is_clean=False, current_branch=current_branch, error=stderr
            )

        uncommitted = [line for line in stdout.split("\n") if line.strip()]
        return GitStatus(
            is_clean=len(uncommitted) == 0,
            current_branch=current_branch,
            uncommitted_files=uncommitted,
        )

    def create_branch(self, branch_name: str) -> bool:
        """Create and checkout a branch, or checkout if it exists"""
        # Check if branch exists
        stdout, _, rc = self.run(
            ["show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
            check=False,
        )

        if rc == 0:
            # Branch exists, checkout
            print(f"  Branch {branch_name} exists, checking out...")
            _, stderr, rc = self.run(["checkout", branch_name])
        else:
            # Create new branch
            print(f"  Creating branch: {branch_name}")
            _, stderr, rc = self.run(["checkout", "-b", branch_name])

        if rc != 0:
            print(f"  ERROR: {stderr}")
            return False
        return True

    def commit(self, message: str, files: list[Path] | None = None) -> bool:
        """Stage files and commit"""
        if files:
            for f in files:
                if f.exists():
                    self.run(["add", str(f)])

        _, stderr, rc = self.run(["commit", "-m", message])
        if rc != 0:
            if "nothing to commit" in stderr:
                print("  No changes to commit")
                return True
            print(f"  ERROR: {stderr}")
            return False
        return True

    def tag(self, tag_name: str, message: str, force: bool = False) -> bool:
        """Create an annotated tag"""
        cmd = ["tag", "-a", tag_name, "-m", message]
        if force:
            cmd.insert(1, "-f")

        _, stderr, rc = self.run(cmd)
        if rc != 0:
            print(f"  ERROR: {stderr}")
            return False
        return True

    def publish_release(self, branch_name: str, tag_name: str) -> bool:
        """Atomically push and verify every ref that constitutes a release."""
        refspecs = [
            "master",
            branch_name,
            f"refs/tags/{tag_name}",
        ]
        _, stderr, rc = self.run(["push", "--atomic", "origin", *refspecs])
        if rc != 0:
            print(f"  ERROR publishing release refs: {stderr}")
            return False

        refs = (
            ("refs/heads/master", "refs/heads/master"),
            (f"refs/heads/{branch_name}", f"refs/heads/{branch_name}"),
            (f"refs/tags/{tag_name}", f"refs/tags/{tag_name}"),
        )
        for local_ref, remote_ref in refs:
            local_sha, local_error, local_rc = self.run(["rev-parse", local_ref])
            remote_line, remote_error, remote_rc = self.run(
                ["ls-remote", "--exit-code", "origin", remote_ref],
                check=False,
            )
            remote_sha = remote_line.split()[0] if remote_line else ""
            if (
                local_rc != 0
                or remote_rc != 0
                or not local_sha
                or local_sha != remote_sha
            ):
                detail = remote_error or local_error or "remote ref differs from local"
                print(f"  ERROR verifying {remote_ref}: {detail}")
                return False

        print(f"  Published master, {branch_name}, and {tag_name} to origin")
        return True

    def merge_to_master(self, source_branch: str, version: str) -> bool:
        """Merge a branch to master"""
        _, stderr, rc = self.run(["checkout", "master"])
        if rc != 0:
            print(f"  WARNING: Could not checkout master: {stderr}")
            return False

        _, stderr, rc = self.run(
            [
                "merge",
                source_branch,
                "--no-ff",
                "-m",
                f"Merge release v{version} to master",
            ]
        )
        if rc != 0:
            print(f"  WARNING: Could not merge to master: {stderr}")
            return False

        print("  Merged to master")
        return True


class Packager:
    """Creates .mpackage files"""

    def __init__(self, version: str):
        self.version = version
        self.releases_dir = PROJECT_ROOT / "Releases"
        self.xml_file = PROJECT_ROOT / "LuminariGUI.xml"

    def get_package_path(self, is_dev: bool = False) -> Path:
        """Get output path for package"""
        if is_dev:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"LuminariGUI-v{self.version}-dev-{timestamp}.mpackage"
        else:
            filename = f"LuminariGUI-v{self.version}.mpackage"
        return self.releases_dir / filename

    def create_config_lua(self) -> str:
        """Generate config.lua content.

        Field names and types follow Mudlet's own package exporter
        (src/dlgPackageExporter.cpp, writeConfigFile):
            mpackage, author, icon, title, description,
            version, helpURL, dependencies, created

        Note: `dependencies` must be a comma-separated STRING, not a Lua
        table. Mudlet's exporter stores the icon under
        `.mudlet/Icon/<filename>` and records only its basename here.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return f'''mpackage = "LuminariGUI"
author = "LuminariMUD Team"
icon = "{PACKAGE_ICON_NAME}"
title = "LuminariGUI"
description = [[
Enhanced MUD client interface for LuminariMUD with advanced features
including chat management, mapping, status effects, and more.
]]
version = "{self.version}"
helpURL = "https://github.com/LuminariMUD/LuminariGUI"
created = "{today}"
dependencies = ""
'''

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def create(self, is_dev: bool = False) -> Path | None:
        """Create a .mpackage file"""
        # Ensure releases directory exists
        self.releases_dir.mkdir(parents=True, exist_ok=True)

        # Validate XML exists
        if not self.xml_file.exists():
            print(f"ERROR: {self.xml_file} not found")
            print("Run 'python build.py' first to generate the XML file")
            return None

        xml_version = get_version_from_xml(self.xml_file)
        if not xml_version:
            print(f"ERROR: Could not read package version from {self.xml_file}")
            return None
        if xml_version != self.version:
            print(
                "ERROR: Refusing to package mismatched versions: "
                f"requested v{self.version}, XML contains v{xml_version}"
            )
            print("Build the requested version first, or omit --version.")
            return None

        output_path = self.get_package_path(is_dev)
        print(
            f"Creating {'development' if is_dev else 'release'} package: {output_path.name}"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy XML file
            shutil.copy2(self.xml_file, temp_path / "LuminariGUI.xml")
            print("  Added: LuminariGUI.xml")

            # Copy images directory
            images_dir = PROJECT_ROOT / "images"
            if images_dir.exists() and images_dir.is_dir():
                shutil.copytree(images_dir, temp_path / "images")
                print("  Added: images/")

            # Match Mudlet's package exporter layout. The package manager
            # resolves config.lua's basename beneath `.mudlet/Icon/`.
            if not PACKAGE_ICON_PATH.is_file():
                print(f"ERROR: Package icon not found: {PACKAGE_ICON_PATH}")
                return None
            icon_dir = temp_path / ".mudlet" / "Icon"
            icon_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PACKAGE_ICON_PATH, icon_dir / PACKAGE_ICON_NAME)
            print(f"  Added: .mudlet/Icon/{PACKAGE_ICON_NAME}")

            # Copy audio directory
            audio_dir = PROJECT_ROOT / "audio"
            if audio_dir.exists() and audio_dir.is_dir():
                shutil.copytree(audio_dir, temp_path / "audio")
                print("  Added: audio/")

            # Create config.lua
            config_lua = temp_path / "config.lua"
            config_lua.write_text(self.create_config_lua(), encoding="utf-8")
            print("  Added: config.lua")

            # Create ZIP archive
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_path.rglob("*"):
                    if file_path.is_file():
                        arc_name = file_path.relative_to(temp_path)
                        zipf.write(file_path, arc_name)

        if output_path.exists():
            size_mb = output_path.stat().st_size / 1024 / 1024
            print(f"Package created: {output_path.name} ({size_mb:.2f} MB)")

            # Create metadata
            metadata = PackageMetadata(
                version=self.version,
                package_type="development" if is_dev else "release",
                created=datetime.now().isoformat(),
                package_file=output_path.name,
                file_size=output_path.stat().st_size,
                sha256=self.calculate_sha256(output_path),
            )

            metadata_path = output_path.with_suffix(".json")
            metadata_path.write_text(
                json.dumps(metadata.to_dict(), indent=2), encoding="utf-8"
            )
            print(f"Metadata created: {metadata_path.name}")

            return output_path

        print("ERROR: Failed to create package")
        return None

    def list_packages(self) -> list[tuple[str, dict[str, Any] | None]]:
        """List all packages in Releases directory"""
        if not self.releases_dir.exists():
            return []

        packages: list[tuple[str, dict[str, Any] | None]] = []
        for pkg in sorted(self.releases_dir.glob("*.mpackage")):
            metadata = None
            metadata_path = pkg.with_suffix(".json")
            if metadata_path.exists():
                try:
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass
            packages.append((pkg.name, metadata))

        return packages

    def clean_dev_packages(self, keep: int = 3) -> int:
        """Remove old dev packages, keeping the latest N"""
        if not self.releases_dir.exists():
            return 0

        dev_pattern = re.compile(r"LuminariGUI-v[\d.]+.*-dev-(\d{8})-(\d{6})\.mpackage")
        dev_packages = []

        for pkg in self.releases_dir.glob("*-dev-*.mpackage"):
            match = dev_pattern.match(pkg.name)
            if match:
                timestamp = datetime.strptime(
                    f"{match.group(1)}-{match.group(2)}", "%Y%m%d-%H%M%S"
                )
                dev_packages.append((timestamp, pkg))

        dev_packages.sort(key=lambda x: x[0], reverse=True)
        removed = 0

        for _, pkg in dev_packages[keep:]:
            try:
                pkg.unlink()
                metadata = pkg.with_suffix(".json")
                if metadata.exists():
                    metadata.unlink()
                print(f"  Removed: {pkg.name}")
                removed += 1
            except OSError as e:
                print(f"  WARNING: Could not remove {pkg.name}: {e}")

        return removed


class ReleaseWorkflow:
    """Manages the full release workflow"""

    def __init__(
        self,
        version: str,
        dry_run: bool = False,
        version_override: str | None = None,
    ):
        self.version = version
        self.version_override = version_override
        self.dry_run = dry_run
        self.git = GitManager()
        self.packager = Packager(version)

    def _set_version(self, version: str) -> None:
        """Keep branch, tag, package metadata, and XML expectations aligned."""
        self.version = version
        self.packager = Packager(version)

    def run_build(self) -> bool:
        """Run build.py to generate fresh XML"""
        print("\n[2/7] Building XML from sources...")
        if self.dry_run:
            target_version = (
                self.version_override
                if self.version_override is not None
                else increment_build_version(self.version)
            )
            self._set_version(target_version)
            print(f"  [DRY RUN] Would build exact version v{target_version}")
            return True

        command = [sys.executable, str(SCRIPT_DIR / "build.py")]
        if self.version_override is not None:
            command.extend(["--version", self.version_override])

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print("  ERROR: Build failed")
            print(result.stderr)
            return False

        built_version = get_version_from_build_yaml()
        if not built_version:
            print("  ERROR: Build completed but build.yaml has no version")
            return False
        if self.version_override is not None and built_version != self.version_override:
            print(
                "  ERROR: Build ignored requested version "
                f"v{self.version_override} and produced v{built_version}"
            )
            return False

        self._set_version(built_version)
        print(f"  Build completed at v{self.version}")
        return True

    def run_tests(self) -> bool:
        """Run test suite"""
        print("\n[3/7] Running test suite...")
        if self.dry_run:
            print("  [DRY RUN] Would run tests")
            return True

        test_runner = PROJECT_ROOT / "tests" / "run_tests.py"
        if not test_runner.exists():
            print("  WARNING: Test runner not found, skipping")
            return True

        result = subprocess.run(
            [sys.executable, str(test_runner), "--skip-optional"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=PROJECT_ROOT / "tests",
        )

        if result.returncode != 0:
            print("  ERROR: Tests failed")
            print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            return False

        print("  Tests passed")
        return True

    def check_git_status(self) -> bool:
        """Check git repository status"""
        print("\n[1/7] Checking git status before build...")
        if self.dry_run:
            print("  [DRY RUN] Would check git status")
            return True

        status = self.git.get_status()
        if status.error:
            print(f"  ERROR: {status.error}")
            return False

        if not status.is_clean:
            print("  WARNING: Uncommitted changes:")
            for f in status.uncommitted_files[:10]:
                print(f"    {f}")
            if len(status.uncommitted_files) > 10:
                print(f"    ... and {len(status.uncommitted_files) - 10} more")
            return False

        print(f"  Repository clean on branch: {status.current_branch}")
        return True

    def check_github_access(self) -> bool:
        """Verify GitHub CLI availability and authentication before mutation."""
        if self.dry_run:
            print("  [DRY RUN] Would verify authenticated GitHub CLI access")
            return True

        gh_path = shutil.which("gh")
        if not gh_path:
            print("  ERROR: GitHub CLI (gh) is required before publishing a release")
            return False

        result = subprocess.run(
            [gh_path, "auth", "status"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            print(f"  ERROR: GitHub CLI is not authenticated: {detail}")
            return False

        print("  GitHub CLI authentication verified")
        return True

    def create_release_branch(self) -> bool:
        """Create release branch"""
        branch_name = f"release/v{self.version}"
        print(f"\n[4/7] Creating release branch: {branch_name}")

        if self.dry_run:
            print(f"  [DRY RUN] Would create branch {branch_name}")
            return True

        if not self.git.create_branch(branch_name):
            return False

        # Commit any build artifacts
        files_to_commit = [
            PROJECT_ROOT / "LuminariGUI.xml",
            PROJECT_ROOT / "theGUI" / "build.yaml",
            PROJECT_ROOT / "docs" / "archive",
        ]

        if not self.git.commit(f"Prepare release v{self.version}", files_to_commit):
            print("  WARNING: Could not commit release changes")

        return True

    def create_package(self) -> bool:
        """Create the release package"""
        print("\n[5/7] Creating release package...")
        if self.dry_run:
            print(f"  [DRY RUN] Would create package v{self.version}")
            return True

        package_path = self.packager.create(is_dev=False)
        if package_path is None:
            return False

        metadata_path = package_path.with_suffix(".json")
        files_to_commit = [package_path, metadata_path]
        if not self.git.commit(f"Add release package v{self.version}", files_to_commit):
            print("  ERROR: Could not commit release package")
            return False

        return True

    def create_tag_merge_and_publish(self) -> bool:
        """Create the tag, merge to master, and publish all release refs."""
        tag_name = f"v{self.version}"
        branch_name = f"release/v{self.version}"
        print(f"\n[6/7] Tagging, merging, and publishing refs: {tag_name}")

        if self.dry_run:
            print(f"  [DRY RUN] Would create tag {tag_name}")
            print(f"  [DRY RUN] Would merge {branch_name} to master")
            print("  [DRY RUN] Would atomically push master, release branch, and tag")
            return True

        # Create tag
        if not self.git.tag(tag_name, f"Release version {self.version}"):
            return False

        # Merge to master
        if not self.git.merge_to_master(branch_name, self.version):
            return False

        print("  Publishing release refs to origin...")
        if not self.git.publish_release(branch_name, tag_name):
            return False

        return True

    def publish_github_release(self) -> bool:
        """Create and verify the public GitHub Release and both assets."""
        tag_name = f"v{self.version}"
        package_path = self.packager.get_package_path(is_dev=False)
        metadata_path = package_path.with_suffix(".json")
        print(f"\n[7/7] Publishing GitHub Release: {tag_name}")

        if self.dry_run:
            print(f"  [DRY RUN] Would publish GitHub Release {tag_name}")
            print(
                f"  [DRY RUN] Would attach {package_path.name} and {metadata_path.name}"
            )
            print("  [DRY RUN] Would verify the release and uploaded assets")
            return True

        if not package_path.exists() or not metadata_path.exists():
            print("  ERROR: Release package or metadata is missing")
            return False

        gh_path = shutil.which("gh")
        if not gh_path:
            print(
                "  ERROR: GitHub CLI (gh) is required to publish a release. "
                "Install and authenticate gh, then retry."
            )
            return False

        create_result = subprocess.run(
            [
                gh_path,
                "release",
                "create",
                tag_name,
                str(package_path),
                str(metadata_path),
                "--title",
                f"LuminariGUI v{self.version}",
                "--generate-notes",
                "--verify-tag",
                "--latest",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if create_result.returncode != 0:
            detail = create_result.stderr.strip() or create_result.stdout.strip()
            print(f"  ERROR publishing GitHub Release: {detail}")
            return False

        view_result = subprocess.run(
            [
                gh_path,
                "release",
                "view",
                tag_name,
                "--json",
                "url,isDraft,isPrerelease,tagName,assets",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if view_result.returncode != 0:
            detail = view_result.stderr.strip() or view_result.stdout.strip()
            print(f"  ERROR verifying GitHub Release: {detail}")
            return False

        try:
            release = json.loads(view_result.stdout)
        except json.JSONDecodeError as error:
            print(f"  ERROR parsing GitHub Release verification: {error}")
            return False

        if release.get("tagName") != tag_name:
            print("  ERROR: GitHub Release tag does not match the package version")
            return False
        if release.get("isDraft"):
            print("  ERROR: GitHub Release is still a draft")
            return False
        if release.get("isPrerelease"):
            print("  ERROR: GitHub Release was unexpectedly marked as a prerelease")
            return False

        assets = {
            asset.get("name"): str(asset.get("state", "")).lower()
            for asset in release.get("assets", [])
        }
        expected_assets = (package_path.name, metadata_path.name)
        for asset_name in expected_assets:
            if assets.get(asset_name) != "uploaded":
                print(f"  ERROR: GitHub Release asset is not uploaded: {asset_name}")
                return False

        release_url = release.get("url") or create_result.stdout.strip()
        print(f"  Published and verified: {release_url}")
        return True

    def execute(
        self,
        skip_build: bool = False,
        skip_tests: bool = False,
        skip_git_check: bool = False,
    ) -> bool:
        """Execute the complete, publishing release workflow."""
        if skip_build or self.version_override is not None:
            print(f"Starting release workflow for v{self.version}")
        else:
            print(
                f"Starting release workflow from v{self.version}; "
                "the build will select the next version"
            )
        if self.dry_run:
            print("DRY RUN MODE - No changes will be made\n")

        # Step 1: Verify the user's tree before the build creates expected changes.
        if not skip_git_check:
            if not self.check_git_status():
                print("\nCommit your changes first, or use --skip-git-check")
                return False
        else:
            print("\n[1/7] Git check skipped")

        if not self.check_github_access():
            return False

        # Step 2: Build
        if not skip_build:
            if not self.run_build():
                return False
        else:
            print("\n[2/7] Build skipped")

        # Step 3: Tests
        if not skip_tests:
            if not self.run_tests():
                return False
        else:
            print("\n[3/7] Tests skipped")

        # Step 4: Release branch
        if not self.create_release_branch():
            return False

        # Step 5: Package
        if not self.create_package():
            return False

        # Step 6: Tag, merge, push, and verify remote refs.
        if not self.create_tag_merge_and_publish():
            return False

        # Step 7: Publish and verify the GitHub Release page and assets.
        if not self.publish_github_release():
            return False

        # Summary
        print(f"\n{'=' * 50}")
        if self.dry_run:
            print(
                f"Release v{self.version} publication preview completed; "
                "no changes made."
            )
        else:
            print(f"Release v{self.version} fully published and verified!")
        print(f"{'=' * 50}")

        return True


def get_version_from_build_yaml() -> str | None:
    """Get version from build.yaml"""
    build_yaml = SCRIPT_DIR / "build.yaml"
    if not build_yaml.exists():
        return None

    content = build_yaml.read_text(encoding="utf-8")
    match = re.search(r'version:\s*"([^"]+)"', content)
    return match.group(1) if match else None


def cmd_create(args):
    """Handle 'create' command"""
    version = args.version or get_version_from_build_yaml()
    if not version:
        print("ERROR: Could not determine version")
        print("Specify with --version or ensure build.yaml exists")
        return 1

    # Run build first unless skipped
    if not args.skip_build:
        print("Building XML from sources...")
        command = [sys.executable, str(SCRIPT_DIR / "build.py")]
        if args.version is not None:
            command.extend(["--version", args.version])

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print("ERROR: Build failed")
            print(result.stderr)
            return 1
        # Re-read version after build (it auto-increments)
        version = get_version_from_build_yaml() or version
        if args.version is not None and version != args.version:
            print(
                "ERROR: Build ignored requested version "
                f"v{args.version} and produced v{version}"
            )
            return 1

    # Run tests unless skipped
    if not args.skip_tests and not args.dev:
        print("Running tests...")
        test_runner = PROJECT_ROOT / "tests" / "run_tests.py"
        if test_runner.exists():
            result = subprocess.run(
                [sys.executable, str(test_runner), "--skip-optional"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=PROJECT_ROOT / "tests",
            )
            if result.returncode != 0:
                print("ERROR: Tests failed")
                print(
                    result.stdout[-1000:]
                    if len(result.stdout) > 1000
                    else result.stdout
                )
                return 1
            print("Tests passed\n")

    packager = Packager(version)
    package_path = packager.create(is_dev=args.dev)

    if package_path:
        print(f"\nPackage ready: {package_path}")
        return 0
    return 1


def cmd_release(args):
    """Handle 'release' command"""
    version = args.version or get_version_from_build_yaml()
    if not version:
        print("ERROR: Could not determine version")
        return 1

    workflow = ReleaseWorkflow(
        version,
        dry_run=args.dry_run,
        version_override=args.version,
    )
    success = workflow.execute(
        skip_build=args.skip_build,
        skip_tests=args.skip_tests,
        skip_git_check=args.skip_git_check,
    )
    return 0 if success else 1


def cmd_list(args):
    """Handle 'list' command"""
    packager = Packager("")
    packages = packager.list_packages()

    if not packages:
        print("No packages found in Releases/")
        return 0

    print(f"Found {len(packages)} package(s):\n")
    for name, metadata in packages:
        print(f"  {name}")
        if metadata:
            print(f"    Version: {metadata.get('version', 'unknown')}")
            print(f"    Type: {metadata.get('type', 'unknown')}")
            print(f"    Created: {metadata.get('created', 'unknown')}")
            print(f"    Size: {metadata.get('file_size', 0) / 1024 / 1024:.2f} MB")
        print()
    return 0


def cmd_clean(args):
    """Handle 'clean' command"""
    packager = Packager("")
    removed = packager.clean_dev_packages(keep=args.keep)
    print(f"Removed {removed} old dev package(s)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="LuminariGUI Package Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  create    Create a package from built XML
  release   Publish refs, GitHub Release page, and both assets
  list      List existing packages
  clean     Remove old development packages

Examples:
  python package.py create                Create a local package
  python package.py create --dev          Create dev package
  python package.py release --dry-run     Preview publication
  python package.py release               Publish a complete release
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # create command
    create_parser = subparsers.add_parser("create", help="Create a package")
    create_parser.add_argument(
        "--dev", action="store_true", help="Create development package with timestamp"
    )
    create_parser.add_argument(
        "--version",
        type=parse_version_argument,
        help="Build and package an exact version",
    )
    create_parser.add_argument(
        "--skip-build", action="store_true", help="Skip building XML (use existing)"
    )
    create_parser.add_argument(
        "--skip-tests", action="store_true", help="Skip running test suite"
    )

    # release command
    release_parser = subparsers.add_parser(
        "release",
        help="Build and publish a complete release",
    )
    release_parser.add_argument(
        "--version",
        type=parse_version_argument,
        help="Build, package, branch, tag, and publish an exact version",
    )
    release_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview publication without making changes",
    )
    release_parser.add_argument(
        "--skip-build", action="store_true", help="Skip building XML"
    )
    release_parser.add_argument(
        "--skip-tests", action="store_true", help="Skip test suite"
    )
    release_parser.add_argument(
        "--skip-git-check", action="store_true", help="Skip git status check"
    )

    # list command
    subparsers.add_parser("list", help="List existing packages")

    # clean command
    clean_parser = subparsers.add_parser("clean", help="Clean old dev packages")
    clean_parser.add_argument(
        "--keep",
        type=int,
        default=3,
        help="Number of dev packages to keep (default: 3)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "create": cmd_create,
        "release": cmd_release,
        "list": cmd_list,
        "clean": cmd_clean,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
