#!/usr/bin/env python3
"""
LuminariGUI Package Creator - Complete Release Management System
Creates versioned .mpackage files with full release workflow automation

Features:
1. Complete release workflow automation (--release)
2. Git integration (branching, tagging, committing, pushing)
3. Version management across XML and CHANGELOG.md
4. XML validation integration
5. Legacy package cleanup and metadata migration
6. Development and release package creation
7. Comprehensive metadata generation
8. Dry-run mode for testing workflows

Usage Examples:
    # Simple package creation
    python3 create_package.py                    # Auto-version release build
    python3 create_package.py --dev             # Development build
    python3 create_package.py --version 2.1.0   # Specific version
    
    # Full release workflow
    python3 create_package.py --release          # Complete release process
    python3 create_package.py --release --dry-run # Test without changes
    python3 create_package.py --release --push   # Release and push to remote
    
    # Individual git operations
    python3 create_package.py --git-branch       # Create release branch
    python3 create_package.py --git-commit       # Commit version updates
    python3 create_package.py --git-tag          # Create release tag
    
    # Maintenance operations
    python3 create_package.py --list             # List all packages
    python3 create_package.py --migrate-metadata # Generate missing metadata
    python3 create_package.py --cleanup-legacy   # Clean up old files

Release Workflow (--release):
1. XML validation and git status check
2. Version updates in XML headers and CHANGELOG.md
3. Release branch creation and commit
4. Package creation with metadata
5. Git tag creation
6. Optional push to remote
"""

import os
import sys
import shutil
import tempfile
import zipfile
from datetime import datetime
import argparse
import re
import hashlib
import json
import subprocess

def get_version_from_changelog():
    """Extract version from CHANGELOG.md"""
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for version patterns like [2.0.0] - must be numeric versions
        versions = re.findall(r'\[([0-9]+\.[0-9]+\.[0-9]+)\]', content)
        
        # Return first semantic version found
        if versions:
            return versions[0]
        
        return "2.0.0"  # Default fallback
    except Exception as e:
        print(f"⚠️  Warning: Could not read CHANGELOG.md: {e}")
        return "2.0.0"

def create_config_lua(version):
    """Create config.lua with proper metadata"""
    return f'''mpackage = "LuminariGUI"
author = "LuminariMUD Team"
title = "LuminariGUI"
description = [[
Enhanced MUD client interface for LuminariMUD with advanced features
including chat management, mapping, status effects, and more.
]]
version = "{version}"
created = "{datetime.now().strftime('%Y-%m-%d')}"
modified = "{datetime.now().strftime('%Y-%m-%d')}"
dependencies = {{}}
'''

def validate_xml_exists(xml_file):
    """Check if XML file exists and is readable"""
    if not os.path.exists(xml_file):
        print(f"❌ Error: {xml_file} not found")
        return False
    
    if not os.path.isfile(xml_file):
        print(f"❌ Error: {xml_file} is not a file")
        return False
    
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            # Read first few lines to check if it's XML
            first_line = f.readline().strip()
            if not first_line.startswith('<?xml'):
                print(f"⚠️  Warning: {xml_file} doesn't appear to be an XML file")
    except Exception as e:
        print(f"❌ Error reading {xml_file}: {e}")
        return False
    
    return True

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⚠️  Warning: Could not calculate hash for {file_path}: {e}")
        return None

def create_release_metadata(version, package_path, is_dev=False):
    """Create release metadata JSON file"""
    metadata = {
        "version": version,
        "type": "development" if is_dev else "release",
        "created": datetime.now().isoformat(),
        "package_file": os.path.basename(package_path),
        "file_size": os.path.getsize(package_path),
        "sha256": calculate_file_hash(package_path),
        "mudlet_version": "4.0+",
        "description": "LuminariGUI package for LuminariMUD"
    }
    
    return metadata

def setup_releases_directory():
    """Ensure Releases directory exists and is properly structured"""
    releases_dir = "Releases"
    
    if not os.path.exists(releases_dir):
        os.makedirs(releases_dir)
        print(f"📁 Created {releases_dir}/ directory")
    
    return releases_dir

def cleanup_old_dev_packages(releases_dir, keep_latest=3):
    """Clean up old development packages, keeping only the latest N"""
    dev_pattern = re.compile(r'LuminariGUI-v([0-9.]+)-dev-(\d{8})-(\d{6})\.mpackage')
    dev_packages = []
    
    for item in os.listdir(releases_dir):
        if os.path.isfile(os.path.join(releases_dir, item)):
            match = dev_pattern.match(item)
            if match:
                version, date, time = match.groups()
                timestamp = datetime.strptime(f"{date}-{time}", "%Y%m%d-%H%M%S")
                dev_packages.append((timestamp, item))
    
    # Sort by timestamp, newest first
    dev_packages.sort(key=lambda x: x[0], reverse=True)
    
    # Remove old packages beyond keep_latest
    if len(dev_packages) > keep_latest:
        for _, package_name in dev_packages[keep_latest:]:
            package_path = os.path.join(releases_dir, package_name)
            metadata_path = package_path.replace('.mpackage', '.json')
            
            try:
                os.remove(package_path)
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                print(f"🗑️  Removed old dev package: {package_name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not remove {package_name}: {e}")

def run_git_command(command, check=True):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(
            ['git'] + command, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.stderr.strip(), e.returncode
    except FileNotFoundError:
        return "", "Git not found", 1

def check_git_status():
    """Check if git repository is clean"""
    stdout, stderr, returncode = run_git_command(['status', '--porcelain'])
    
    if returncode != 0:
        print(f"⚠️  Warning: Git status check failed: {stderr}")
        return False
    
    if stdout.strip():
        print("⚠️  Warning: Git repository has uncommitted changes:")
        for line in stdout.strip().split('\n'):
            print(f"    {line}")
        return False
    
    return True

def get_current_branch():
    """Get current git branch"""
    stdout, stderr, returncode = run_git_command(['branch', '--show-current'])
    
    if returncode != 0:
        print(f"⚠️  Warning: Could not get current branch: {stderr}")
        return None
    
    return stdout

def create_release_branch(version):
    """Create and checkout a release branch"""
    branch_name = f"release/v{version}"
    
    # Check if branch already exists
    stdout, stderr, returncode = run_git_command(['show-ref', '--verify', '--quiet', f'refs/heads/{branch_name}'], check=False)
    
    if returncode == 0:
        print(f"🌿 Release branch {branch_name} already exists, checking out...")
        stdout, stderr, returncode = run_git_command(['checkout', branch_name])
        if returncode != 0:
            print(f"❌ Error checking out branch {branch_name}: {stderr}")
            return False
    else:
        print(f"🌿 Creating release branch: {branch_name}")
        stdout, stderr, returncode = run_git_command(['checkout', '-b', branch_name])
        if returncode != 0:
            print(f"❌ Error creating branch {branch_name}: {stderr}")
            return False
    
    return True

def commit_release_changes(version, files_to_add=None):
    """Commit release-related changes"""
    if files_to_add is None:
        files_to_add = ['CHANGELOG.md', 'LuminariGUI.xml']
    
    # Add specified files
    for file_path in files_to_add:
        if os.path.exists(file_path):
            stdout, stderr, returncode = run_git_command(['add', file_path])
            if returncode != 0:
                print(f"⚠️  Warning: Could not add {file_path}: {stderr}")
    
    # Create commit
    commit_message = f"Prepare release v{version}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
    
    stdout, stderr, returncode = run_git_command(['commit', '-m', commit_message])
    if returncode != 0:
        if "nothing to commit" in stderr:
            print("📝 No changes to commit")
            return True
        else:
            print(f"❌ Error committing changes: {stderr}")
            return False
    
    print(f"📝 Committed release changes for v{version}")
    return True

def create_git_tag(version, force=False):
    """Create and push a git tag for the release"""
    tag_name = f"v{version}"
    
    # Check if tag already exists
    stdout, stderr, returncode = run_git_command(['show-ref', '--tags', '--quiet', f'refs/tags/{tag_name}'], check=False)
    
    if returncode == 0 and not force:
        print(f"⚠️  Tag {tag_name} already exists. Use --force-tag to overwrite.")
        return False
    
    # Create annotated tag
    tag_message = f"Release version {version}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)"
    
    cmd = ['tag', '-a', tag_name, '-m', tag_message]
    if force:
        cmd.insert(1, '-f')
    
    stdout, stderr, returncode = run_git_command(cmd)
    if returncode != 0:
        print(f"❌ Error creating tag {tag_name}: {stderr}")
        return False
    
    print(f"🏷️  Created git tag: {tag_name}")
    return True

def push_git_changes(branch_name=None, push_tags=False):
    """Push changes and optionally tags to remote"""
    if branch_name:
        stdout, stderr, returncode = run_git_command(['push', 'origin', branch_name])
        if returncode != 0:
            print(f"❌ Error pushing branch {branch_name}: {stderr}")
            return False
        print(f"📤 Pushed branch: {branch_name}")
    
    if push_tags:
        stdout, stderr, returncode = run_git_command(['push', 'origin', '--tags'])
        if returncode != 0:
            print(f"❌ Error pushing tags: {stderr}")
            return False
        print("📤 Pushed tags to remote")
    
    return True

def validate_package_file(xml_file="LuminariGUI.xml", run_tests=False):
    """Run package validation using validate_package.py and optionally full test suite"""
    if not os.path.exists("validate_package.py"):
        print("⚠️  Warning: validate_package.py not found, skipping package validation")
        return True
    
    try:
        # Run XML validation (now includes Lua syntax checking)
        result = subprocess.run(
            [sys.executable, "validate_package.py", xml_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ XML validation passed")
            xml_validation_passed = True
        else:
            print("❌ XML validation failed:")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            xml_validation_passed = False
    except Exception as e:
        print(f"❌ Error running XML validation: {e}")
        xml_validation_passed = False
    
    # Run full test suite if requested
    test_suite_passed = True
    if run_tests:
        print("\n🧪 Running full test suite...")
        if os.path.exists("run_tests.py"):
            try:
                result = subprocess.run(
                    [sys.executable, "run_tests.py", "--xml", xml_file, "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print("✅ Test suite passed")
                    test_suite_passed = True
                else:
                    print("❌ Test suite failed:")
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(result.stderr)
                    test_suite_passed = False
            except subprocess.TimeoutExpired:
                print("❌ Test suite timed out after 5 minutes")
                test_suite_passed = False
            except Exception as e:
                print(f"❌ Error running test suite: {e}")
                test_suite_passed = False
        else:
            print("⚠️  Warning: run_tests.py not found, skipping test suite")
    
    return xml_validation_passed and test_suite_passed

def update_xml_version(xml_file, version):
    """Update version in XML file header comment"""
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update version in header comment (pattern: <!-- LuminariGUI Package v2.1.0)
        version_pattern = r'(<!--\s*LuminariGUI\s+Package\s+v)([0-9]+\.[0-9]+\.[0-9]+)'
        new_version_line = f'\\g<1>{version}'
        
        updated_content = re.sub(version_pattern, new_version_line, content, flags=re.IGNORECASE)
        
        if updated_content != content:
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated version in {xml_file} to v{version}")
            return True
        else:
            print(f"⚠️  Warning: Could not find version pattern in {xml_file}")
            return False
    except Exception as e:
        print(f"❌ Error updating XML version: {e}")
        return False

def update_changelog_version(version):
    """Update CHANGELOG.md by moving unreleased items to new version section"""
    try:
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if version already exists
        if f"## [{version}]" in content:
            print(f"⚠️  Version {version} already exists in CHANGELOG.md")
            return True
        
        # Find unreleased section and move items to new version
        today = datetime.now().strftime('%Y-%m-%d')
        new_version_header = f"## [{version}] - {today}"
        
        # Pattern to match ## [Unreleased] section
        unreleased_pattern = r'(## \[Unreleased\]\s*\n)(.*?)(\n## \[)'
        
        def replace_unreleased(match):
            header = match.group(1)
            unreleased_content = match.group(2).strip()
            next_section = match.group(3)
            
            if unreleased_content:
                # Move content to new version section
                return f"{header}\n\n{new_version_header}\n\n{unreleased_content}\n{next_section}"
            else:
                # Just add empty version section
                return f"{header}\n\n{new_version_header}\n\n### Added\n- Release version {version}\n{next_section}"
        
        updated_content = re.sub(unreleased_pattern, replace_unreleased, content, flags=re.DOTALL)
        
        if updated_content != content:
            with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated CHANGELOG.md with version {version}")
            return True
        else:
            print("⚠️  Warning: Could not update CHANGELOG.md")
            return False
    except Exception as e:
        print(f"❌ Error updating changelog: {e}")
        return False

def check_version_consistency(version, xml_file="LuminariGUI.xml"):
    """Check if version is consistent across files"""
    changelog_version = get_version_from_changelog()
    
    print(f"🔍 Version consistency check:")
    print(f"   Requested version: {version}")
    print(f"   CHANGELOG.md version: {changelog_version}")
    
    # Check XML version
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        xml_version_match = re.search(r'LuminariGUI\s+Package\s+v([0-9]+\.[0-9]+\.[0-9]+)', xml_content, re.IGNORECASE)
        if xml_version_match:
            xml_version = xml_version_match.group(1)
            print(f"   {xml_file} version: {xml_version}")
            
            if version == xml_version == changelog_version:
                print("✅ All versions are consistent")
                return True
            else:
                print("⚠️  Version inconsistency detected")
                return False
        else:
            print(f"⚠️  Could not find version in {xml_file}")
            return False
    except Exception as e:
        print(f"❌ Error checking XML version: {e}")
        return False

def migrate_legacy_packages():
    """Generate metadata for existing packages that don't have .json files"""
    releases_dir = "Releases"
    
    if not os.path.exists(releases_dir):
        print("📁 No Releases directory found")
        return
    
    migrated_count = 0
    
    for item in os.listdir(releases_dir):
        if item.endswith('.mpackage'):
            package_path = os.path.join(releases_dir, item)
            metadata_path = package_path.replace('.mpackage', '.json')
            
            # Skip if metadata already exists
            if os.path.exists(metadata_path):
                continue
            
            print(f"📋 Generating metadata for: {item}")
            
            # Try to extract version from filename
            version_match = re.search(r'v([0-9]+\.[0-9]+\.[0-9]+)', item)
            if version_match:
                version = version_match.group(1)
            else:
                version = "unknown"
            
            # Determine if it's a dev build
            is_dev = "-dev-" in item
            
            # Create metadata
            metadata = create_release_metadata(version, package_path, is_dev)
            
            try:
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                print(f"✅ Created metadata: {os.path.basename(metadata_path)}")
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error creating metadata for {item}: {e}")
    
    if migrated_count > 0:
        print(f"🎉 Migrated {migrated_count} package(s) to include metadata")
    else:
        print("✅ All packages already have metadata")

def cleanup_legacy_files():
    """Clean up old files and organize releases directory"""
    releases_dir = "Releases"
    
    if not os.path.exists(releases_dir):
        return
    
    legacy_files = []
    
    # Find files that don't follow the new naming convention
    for item in os.listdir(releases_dir):
        item_path = os.path.join(releases_dir, item)
        
        if os.path.isfile(item_path):
            # Check for old naming patterns
            if (item == "LuminariGUI.mpackage" or 
                item == "LuminariGUI.xml.backup" or
                (item.endswith('.mpackage') and not re.match(r'LuminariGUI-v[0-9]+\.[0-9]+\.[0-9]+.*\.mpackage', item))):
                legacy_files.append(item)
    
    if legacy_files:
        print(f"🧹 Found {len(legacy_files)} legacy file(s) to clean up:")
        for file in legacy_files:
            print(f"   {file}")
        
        response = input("Remove these files? (y/N): ")
        if response.lower() == 'y':
            for file in legacy_files:
                try:
                    os.remove(os.path.join(releases_dir, file))
                    print(f"🗑️  Removed: {file}")
                except Exception as e:
                    print(f"❌ Error removing {file}: {e}")
        else:
            print("⏭️  Skipped cleanup")
    else:
        print("✅ No legacy files found")

def execute_release_workflow(xml_file, version, dry_run=False, push=False, force_tag=False, skip_validation=False, skip_git_check=False, run_tests=False):
    """Execute complete release workflow"""
    print(f"🚀 Starting release workflow for version {version}")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    # Step 1: Pre-release validation
    print("\n📋 Step 1: Pre-release validation")
    
    if not skip_validation:
        print("   Validating XML...")
        if dry_run:
            print("   [DRY RUN] Would validate XML")
        else:
            if not validate_package_file(xml_file, run_tests):
                print("❌ Release aborted due to validation failure")
                return False
    
    if not skip_git_check:
        print("   Checking git status...")
        if dry_run:
            print("   [DRY RUN] Would check git status")
        else:
            if not check_git_status():
                print("❌ Release aborted due to uncommitted changes")
                print("💡 Commit your changes or use --skip-git-check")
                return False
    
    # Step 2: Version management
    print("\n📝 Step 2: Version management")
    
    print("   Checking version consistency...")
    if dry_run:
        print(f"   [DRY RUN] Would check version consistency for {version}")
    else:
        check_version_consistency(version, xml_file)
    
    print("   Updating XML version...")
    if dry_run:
        print(f"   [DRY RUN] Would update {xml_file} to version {version}")
    else:
        if not update_xml_version(xml_file, version):
            print("⚠️  Warning: Could not update XML version")
    
    print("   Updating CHANGELOG.md...")
    if dry_run:
        print(f"   [DRY RUN] Would update CHANGELOG.md for version {version}")
    else:
        if not update_changelog_version(version):
            print("⚠️  Warning: Could not update CHANGELOG.md")
    
    # Step 3: Git workflow
    print("\n🌿 Step 3: Git workflow")
    
    original_branch = get_current_branch()
    release_branch = f"release/v{version}"
    
    print(f"   Creating release branch: {release_branch}")
    if dry_run:
        print(f"   [DRY RUN] Would create and checkout branch {release_branch}")
    else:
        if not create_release_branch(version):
            print("❌ Release aborted due to git branch creation failure")
            return False
    
    print("   Committing changes...")
    if dry_run:
        print(f"   [DRY RUN] Would commit changes for version {version}")
    else:
        if not commit_release_changes(version):
            print("⚠️  Warning: Could not commit changes")
    
    # Step 4: Package creation
    print("\n📦 Step 4: Package creation")
    
    print("   Creating release package...")
    if dry_run:
        print(f"   [DRY RUN] Would create package for version {version}")
        package_created = True
    else:
        package_created = create_mpackage(xml_file, version, is_dev=False)
        if not package_created:
            print("❌ Release aborted due to package creation failure")
            return False
    
    # Step 5: Git tagging
    print("\n🏷️  Step 5: Git tagging")
    
    print(f"   Creating git tag: v{version}")
    if dry_run:
        print(f"   [DRY RUN] Would create git tag v{version}")
    else:
        if not create_git_tag(version, force=force_tag):
            print("⚠️  Warning: Could not create git tag")
    
    # Step 6: Push to remote (optional)
    if push:
        print("\n📤 Step 6: Push to remote")
        
        print(f"   Pushing branch: {release_branch}")
        if dry_run:
            print(f"   [DRY RUN] Would push branch {release_branch}")
        else:
            if not push_git_changes(release_branch, push_tags=True):
                print("⚠️  Warning: Could not push to remote")
    
    # Summary
    print(f"\n✅ Release workflow completed for version {version}")
    
    if not dry_run:
        print("\n💡 Next steps:")
        print("   1. Test the package in Mudlet")
        print("   2. Create GitHub release with release notes")
        if not push:
            print("   3. Push changes to remote when ready:")
            print(f"      git push origin {release_branch}")
            print("      git push origin --tags")
        print(f"   4. Merge {release_branch} to main branch when ready")
    
    return True

def create_mpackage(xml_file="LuminariGUI.xml", version=None, is_dev=False):
    """Create .mpackage file from XML source with proper versioning"""
    
    # Validate source file
    if not validate_xml_exists(xml_file):
        return False
    
    # Get version from changelog if not provided
    if version is None:
        version = get_version_from_changelog()
    
    # Setup releases directory
    releases_dir = setup_releases_directory()
    
    # Generate output filename
    if is_dev:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f"LuminariGUI-v{version}-dev-{timestamp}.mpackage"
    else:
        output_file = f"LuminariGUI-v{version}.mpackage"
    
    output_path = os.path.join(releases_dir, output_file)
    
    print(f"📦 Creating {'development' if is_dev else 'release'} package version: {version}")
    print(f"📂 Output: {output_path}")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🔧 Working in temporary directory: {temp_dir}")
        
        # Copy XML file
        try:
            shutil.copy2(xml_file, temp_dir)
            print(f"✅ Copied {xml_file}")
        except Exception as e:
            print(f"❌ Error copying {xml_file}: {e}")
            return False
        
        # Copy images directory if it exists
        images_dir = "images"
        if os.path.exists(images_dir) and os.path.isdir(images_dir):
            try:
                shutil.copytree(images_dir, os.path.join(temp_dir, "images"))
                print(f"✅ Copied {images_dir}/ directory")
            except Exception as e:
                print(f"⚠️  Warning: Could not copy images directory: {e}")
        else:
            print(f"⚠️  Warning: {images_dir}/ directory not found, skipping")
        
        # Create config.lua
        config_content = create_config_lua(version)
        config_path = os.path.join(temp_dir, "config.lua")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            print(f"✅ Created config.lua")
        except Exception as e:
            print(f"❌ Error creating config.lua: {e}")
            return False
        
        # Create ZIP archive (which IS the .mpackage file)
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_path)
                        print(f"📁 Added: {arc_path}")
        except Exception as e:
            print(f"❌ Error creating ZIP archive: {e}")
            return False
    
    # Verify the package was created
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"✅ Package created successfully: {output_path} ({size_mb:.1f} MB)")
        
        # Create release metadata
        metadata = create_release_metadata(version, output_path, is_dev)
        metadata_path = output_path.replace('.mpackage', '.json')
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            print(f"📋 Created metadata: {metadata_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create metadata: {e}")
        
        # Show package contents
        print("\n📋 Package contents:")
        try:
            with zipfile.ZipFile(output_path, 'r') as zipf:
                total_files = 0
                total_size = 0
                for info in zipf.infolist():
                    print(f"   {info.filename} ({info.file_size:,} bytes)")
                    total_files += 1
                    total_size += info.file_size
                print(f"\n📊 Total: {total_files} files, {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        except Exception as e:
            print(f"⚠️  Warning: Could not list package contents: {e}")
        
        # Clean up old development packages if this is a dev build
        if is_dev:
            cleanup_old_dev_packages(releases_dir)
        
        return True
    else:
        print(f"❌ Failed to create package: {output_path}")
        return False

def list_releases():
    """List all packages in the Releases directory"""
    releases_dir = "Releases"
    
    if not os.path.exists(releases_dir):
        print("📁 No Releases directory found")
        return
    
    packages = []
    for item in os.listdir(releases_dir):
        if item.endswith('.mpackage'):
            package_path = os.path.join(releases_dir, item)
            metadata_path = package_path.replace('.mpackage', '.json')
            
            # Try to load metadata
            metadata = None
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            packages.append((item, package_path, metadata))
    
    if not packages:
        print("📦 No packages found in Releases/")
        return
    
    print(f"📦 Found {len(packages)} package(s) in Releases/:")
    for package_name, package_path, metadata in sorted(packages):
        size_mb = os.path.getsize(package_path) / 1024 / 1024
        if metadata:
            version = metadata.get('version', 'unknown')
            pkg_type = metadata.get('type', 'unknown')
            created = metadata.get('created', 'unknown')
            print(f"   {package_name}")
            print(f"     Version: {version} ({pkg_type})")
            print(f"     Created: {created}")
            print(f"     Size: {size_mb:.1f} MB")
            if 'sha256' in metadata:
                print(f"     SHA256: {metadata['sha256'][:16]}...")
        else:
            print(f"   {package_name} ({size_mb:.1f} MB) - no metadata")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='Create versioned .mpackage files with release management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 create_package.py                         # Release build with auto-version
  python3 create_package.py --version 2.1.0        # Release build with specific version
  python3 create_package.py --dev                  # Development build with timestamp
  python3 create_package.py --release              # Full release workflow
  python3 create_package.py --list                 # List existing releases
  python3 create_package.py --migrate-metadata     # Generate missing metadata files
  python3 create_package.py --cleanup-legacy       # Clean up old files
  
Release Workflow (--release):
  1. Validate XML and check git status
  2. Update version in XML and CHANGELOG.md
  3. Create release branch and commit changes
  4. Create package and metadata
  5. Create git tag
  6. Push changes (if --push specified)
  
Output Structure:
  Releases/
    ├── LuminariGUI-v2.1.0.mpackage           # Release packages
    ├── LuminariGUI-v2.1.0.json               # Release metadata
    ├── LuminariGUI-v2.1.1-dev-20240115-143022.mpackage  # Dev packages
    └── LuminariGUI-v2.1.1-dev-20240115-143022.json      # Dev metadata
'''
    )
    
    # Core options
    parser.add_argument('--xml', default='LuminariGUI.xml', 
                       help='Source XML file (default: LuminariGUI.xml)')
    parser.add_argument('--version', 
                       help='Override version (default: auto-detect from CHANGELOG.md)')
    parser.add_argument('--dev', action='store_true',
                       help='Create development build with timestamp')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    # Release workflow
    parser.add_argument('--release', action='store_true',
                       help='Full release workflow: validation, versioning, git workflow, packaging')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without executing (for --release)')
    
    # Git integration
    parser.add_argument('--git-tag', action='store_true',
                       help='Create and push git tag for release')
    parser.add_argument('--git-branch', action='store_true',
                       help='Create release branch')
    parser.add_argument('--git-commit', action='store_true',
                       help='Commit version updates')
    parser.add_argument('--push', action='store_true',
                       help='Push changes to remote (requires git options)')
    parser.add_argument('--force-tag', action='store_true',
                       help='Force overwrite existing git tag')
    
    # Maintenance operations
    parser.add_argument('--list', action='store_true',
                       help='List existing packages in Releases/')
    parser.add_argument('--migrate-metadata', action='store_true',
                       help='Generate metadata for packages missing .json files')
    parser.add_argument('--cleanup-legacy', action='store_true',
                       help='Clean up old/legacy files in Releases/')
    
    # Validation
    # Testing options
    parser.add_argument('--run-tests', action='store_true',
                       help='Run full test suite before package creation')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip XML validation (use with caution)')
    parser.add_argument('--skip-git-check', action='store_true',
                       help='Skip git status check (use with caution)')
    
    args = parser.parse_args()
    
    print("🚀 LuminariGUI Package Creator - Enhanced Release System")
    print("=" * 60)
    
    # Handle maintenance operations first
    if args.list:
        list_releases()
        return
    
    if args.migrate_metadata:
        migrate_legacy_packages()
        return
    
    if args.cleanup_legacy:
        cleanup_legacy_files()
        return
    
    # Get version for operations that need it
    version = args.version or get_version_from_changelog()
    
    if args.verbose:
        print(f"📂 Source XML: {args.xml}")
        print(f"🔢 Version: {version}")
        print(f"🔨 Build type: {'development' if args.dev else 'release'}")
        print()
    
    # Handle release workflow
    if args.release:
        print(f"🎯 Executing full release workflow for version {version}")
        
        success = execute_release_workflow(
            xml_file=args.xml,
            version=version,
            dry_run=args.dry_run,
            push=args.push,
            force_tag=args.force_tag,
            skip_validation=args.skip_validation,
            skip_git_check=args.skip_git_check,
            run_tests=args.run_tests
        )
        
        if not success:
            print("\n❌ Release workflow failed!")
            sys.exit(1)
        return
    
    # Handle individual git operations
    git_operations_performed = False
    
    if args.git_branch:
        print(f"🌿 Creating release branch for version {version}")
        if create_release_branch(version):
            git_operations_performed = True
        else:
            print("❌ Failed to create release branch")
            sys.exit(1)
    
    if args.git_commit:
        print(f"📝 Committing changes for version {version}")
        if commit_release_changes(version):
            git_operations_performed = True
        else:
            print("❌ Failed to commit changes")
            sys.exit(1)
    
    if args.git_tag:
        print(f"🏷️  Creating git tag for version {version}")
        if create_git_tag(version, force=args.force_tag):
            git_operations_performed = True
        else:
            print("❌ Failed to create git tag")
            sys.exit(1)
    
    if args.push and git_operations_performed:
        current_branch = get_current_branch()
        print(f"📤 Pushing changes to remote")
        if not push_git_changes(current_branch, push_tags=True):
            print("❌ Failed to push changes")
            sys.exit(1)
    
    # Handle package creation (default behavior)
    if not git_operations_performed or args.dev or not (args.git_branch or args.git_commit or args.git_tag):
        print(f"📦 Creating package for version {version}")
        
        # Run XML validation unless skipped
        if not args.skip_validation:
            if not validate_package_file(args.xml, args.run_tests):
                print("❌ Package creation aborted due to validation failure")
                sys.exit(1)
        
        success = create_mpackage(args.xml, version, args.dev)
        
        if success:
            print("\n✅ Package creation completed successfully!")
            print("📁 Package saved to Releases/ directory")
            
            if not args.dev:
                print("\n💡 Next steps:")
                print("   1. Test the package in Mudlet")
                print("   2. Update CHANGELOG.md with release notes")
                print("   3. Create git tag: python3 create_package.py --git-tag")
                print("   4. Push to remote: python3 create_package.py --push")
                print("   5. Create GitHub release")
        else:
            print("\n❌ Package creation failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()