#!/usr/bin/env python3
"""Audit runtime handler and timer ownership in assembled package sources.

The old report compared lexical create/kill counts. That incorrectly labeled
every Mudlet one-shot timer as a leak and missed registrations made through
wrapper functions. This analyzer assembles the current source tree in memory,
classifies package/XML-owned and runtime-owned resources, and reports only raw
runtime registrations outside the central ownership manager as unowned.
"""

import argparse
import importlib.util
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = PROJECT_ROOT / "theGUI" / "build.py"
RESOURCE_MANAGER_SCRIPT = "Resource Ownership"
RECURRING_TIMER_NAMES = {"yatco.blink"}


def assemble_source_xml():
    """Build current fragments in memory without changing the repository."""
    spec = importlib.util.spec_from_file_location(
        "luminari_handler_audit_build",
        BUILD_SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load theGUI/build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    build_log = io.StringIO()
    with redirect_stdout(build_log):
        success, assembled = module.Builder(module.BuildConfig()).build(
            validate_only=True
        )
    if not success:
        raise RuntimeError(
            "source assembly failed:\n" + build_log.getvalue().strip()
        )
    return assembled


def load_root(xml_path=None):
    if xml_path:
        return ET.parse(xml_path).getroot()
    return ET.fromstring(assemble_source_xml())


def logical_handler_count(script_name, source):
    """Count registrations hidden behind the package's ownership wrappers."""
    if script_name == "MSDPMapper":
        return len(
            re.findall(r'registerFileScopeHandler\s*\(\s*["\']', source)
        )
    if script_name == "GUI Lifecycle":
        return len(
            re.findall(r'registerLifecycleHandler\s*\(\s*["\']', source)
        )
    if script_name == "GUI Event Registry":
        table_source = source.split(
            "function GUI.unregisterEventHandlers", 1
        )[0]
        return len(
            re.findall(r'^\s*\[["\'][^"\']+["\']\]\s*=', table_source, re.M)
        )
    return 0


def timer_names(source):
    return re.findall(
        r'GUI\.setOwnedTimer\s*\(\s*["\']([^"\']+)["\']',
        source,
    )


def raw_registration_count(source, primitive):
    direct = rf'\b{primitive}\s*\('
    through_pcall = rf'\bpcall\s*\(\s*{primitive}\b'
    return len(re.findall(direct, source)) + len(
        re.findall(through_pcall, source)
    )


def classify_script(script):
    name = script.findtext("name") or "unnamed"
    source = script.findtext("script") or ""
    xml_handlers = len(script.findall("./eventHandlerList/string"))
    owned_handlers = logical_handler_count(name, source)
    owned_timer_names = timer_names(source)
    recurring_timers = sum(
        timer_name in RECURRING_TIMER_NAMES
        for timer_name in owned_timer_names
    )

    raw_handlers = raw_registration_count(
        source,
        "registerAnonymousEventHandler",
    )
    raw_timers = raw_registration_count(source, "tempTimer")
    manager = name == RESOURCE_MANAGER_SCRIPT
    unowned_handlers = 0 if manager else raw_handlers
    unowned_timers = 0 if manager else raw_timers

    if unowned_handlers or unowned_timers:
        status = "UNOWNED"
    elif manager:
        status = "ownership manager"
    elif recurring_timers:
        status = "owned recurring"
    elif owned_timer_names:
        status = "owned one-shot"
    elif xml_handlers:
        status = "package XML"
    else:
        status = "owned handlers"

    return {
        "script": name,
        "owned_handlers": owned_handlers,
        "xml_handlers": xml_handlers,
        "owned_timers": len(owned_timer_names),
        "recurring_timers": recurring_timers,
        "timer_names": owned_timer_names,
        "unowned_handlers": unowned_handlers,
        "unowned_timers": unowned_timers,
        "status": status,
    }


def analyze(root):
    results = []
    for script in root.iter("Script"):
        result = classify_script(script)
        if any(
            result[key]
            for key in (
                "owned_handlers",
                "xml_handlers",
                "owned_timers",
                "unowned_handlers",
                "unowned_timers",
            )
        ) or result["script"] == RESOURCE_MANAGER_SCRIPT:
            results.append(result)

    totals = {
        key: sum(result[key] for result in results)
        for key in (
            "owned_handlers",
            "xml_handlers",
            "owned_timers",
            "recurring_timers",
            "unowned_handlers",
            "unowned_timers",
        )
    }
    return {"scripts": results, "totals": totals}


def print_text(report):
    header = (
        f"{'Script':<30} | {'Handlers owned/XML':<20} | "
        f"{'Timer sites/unowned':<20} | Status"
    )
    print(header)
    print("-" * len(header))
    for result in report["scripts"]:
        handlers = (
            f"{result['owned_handlers']}/{result['xml_handlers']}"
        )
        timers = (
            f"{result['owned_timers']}/{result['unowned_timers']}"
        )
        print(
            f"{result['script']:<30} | {handlers:<20} | "
            f"{timers:<20} | {result['status']}"
        )

    totals = report["totals"]
    print()
    print(
        "Owned runtime handlers: "
        f"{totals['owned_handlers']} "
        f"(+ {totals['xml_handlers']} package/XML-owned)"
    )
    print(
        "Owned timer creation sites: "
        f"{totals['owned_timers']} "
        f"({totals['recurring_timers']} recurring)"
    )
    print(f"Unowned runtime handlers: {totals['unowned_handlers']}")
    print(f"Unowned runtime timers: {totals['unowned_timers']}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Audit LuminariGUI handler and timer ownership"
    )
    parser.add_argument(
        "--xml",
        type=Path,
        help="analyze an explicit built XML instead of assembling sources",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable JSON",
    )
    parser.add_argument(
        "--fail-on-unowned",
        action="store_true",
        help="exit non-zero when a raw unowned registration is found",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        report = analyze(load_root(args.xml))
    except (ET.ParseError, OSError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)

    totals = report["totals"]
    if args.fail_on_unowned and (
        totals["unowned_handlers"] or totals["unowned_timers"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
