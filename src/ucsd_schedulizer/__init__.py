"""Command-line interface for ucsd-schedulizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ics import write_calendar
from .parse import parse_course_list
from .scraper import fetch_schedule
from .select import format_section, print_sections_by_professor, select_schedule
from .terms import list_terms, parse_term


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucsd-schedulizer",
        description=(
            "Build a Google Calendar–ready schedule from UCSD course codes. "
            "Fetches meeting times from the Schedule of Classes and writes schedule.ics."
        ),
    )
    parser.add_argument(
        "quarter",
        nargs="?",
        help="Quarter code or name, e.g. SP26 or 'Spring Quarter 2026'",
    )
    parser.add_argument(
        "-c",
        "--classes",
        help='Comma-separated course codes, e.g. "MATH 20E, DSC 190"',
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Show sections grouped by professor (no calendar file)",
    )
    parser.add_argument(
        "--list-terms",
        action="store_true",
        help="List supported quarters and exit",
    )
    return parser


def _print_summary(sections: list) -> None:
    print("\nYour schedule:")
    for section in sections:
        print(f"  • {section.course_code}: {format_section(section)}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_terms:
        print("Supported quarters:")
        for term in list_terms():
            print(f"  {term.code:5}  {term.name}  ({term.start} → {term.end})")
        return 0

    if not args.quarter or not args.classes:
        parser.error("quarter and -c/--classes are required (unless using --list-terms)")

    try:
        term = parse_term(args.quarter)
        requested = parse_course_list(args.classes)
        courses = fetch_schedule(term.code, requested)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    include_types = {"LE", "DI", "LA"}

    if args.list:
        print(f"{term.name} ({term.code})")
        print_sections_by_professor(courses, requested, include_types=include_types)
        return 0

    print(f"Building schedule for {term.name}...")
    sections = select_schedule(courses, requested, include_types=include_types)

    if not sections:
        print("No sections selected.", file=sys.stderr)
        return 1

    _print_summary(sections)

    output = Path("schedule.ics")
    write_calendar(sections, term, output)
    print(f"\nWrote {output.resolve()}")
    print("\nTo add to Google Calendar:")
    print("  1. Open Google Calendar → Settings → Import & export → Import")
    print(f"  2. Select {output.resolve()}")
    print("  3. Choose which calendar to add events to")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
