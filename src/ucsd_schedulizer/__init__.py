"""Command-line interface for ucsd-schedulizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .ics import write_calendar
from .parse import filter_sections, parse_course_list
from .scraper import fetch_schedule
from .terms import list_terms, parse_term


def _print_sections(sections: list) -> None:
    print("\nFound sections:")
    print(f"{'Course':<14} {'Type':<4} {'Sec':<5} {'Days':<8} {'Time':<14} {'Location':<16} Instructor")
    print("-" * 90)
    for section in sections:
        if section.cancelled:
            continue
        meeting = section.meeting
        days = ""
        time = ""
        if meeting:
            day_names = ["M", "Tu", "W", "Th", "F", "S", "Su"]
            days = "".join(day_names[d] for d in meeting.days)
            sh, sm = divmod(meeting.start_minutes, 60)
            eh, em = divmod(meeting.end_minutes, 60)
            time = f"{sh}:{sm:02d}-{eh}:{em:02d}"
        location = " ".join(filter(None, [section.building, section.room])) or "TBA"
        instructor = section.instructor or ""
        print(
            f"{section.course_code:<14} {section.section_type:<4} {section.section_code:<5} "
            f"{days:<8} {time:<14} {location:<16} {instructor}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucsd-schedulizer",
        description=(
            "Build a Google Calendar–ready schedule from UCSD course codes. "
            "Fetches meeting times from the Schedule of Classes and writes an .ics file."
        ),
    )
    parser.add_argument(
        "quarter",
        nargs="?",
        help="Quarter name or code, e.g. 'SP26' or 'Spring Quarter 2026'",
    )
    parser.add_argument(
        "courses",
        nargs="?",
        help="Comma-separated course codes, e.g. 'DSC 190, CSE 100'",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("schedule.ics"),
        help="Output .ics file path (default: schedule.ics)",
    )
    parser.add_argument(
        "--sections",
        help="Comma-separated section codes to include, e.g. 'A00,B01,C00'",
    )
    parser.add_argument(
        "--types",
        default="LE,DI,LA",
        help="Section types to include (default: LE,DI,LA)",
    )
    parser.add_argument(
        "--list-terms",
        action="store_true",
        help="List supported quarters and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print found sections without writing a calendar file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_terms:
        print("Supported quarters:")
        for term in list_terms():
            print(f"  {term.code:5}  {term.name}  ({term.start} → {term.end})")
        return 0

    if not args.quarter or not args.courses:
        parser.error("quarter and courses are required unless using --list-terms")

    try:
        term = parse_term(args.quarter)
        courses = fetch_schedule(term.code, args.courses)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    include_types = {part.strip().upper() for part in args.types.split(",") if part.strip()}
    section_codes = None
    if args.sections:
        section_codes = {part.strip().upper() for part in args.sections.split(",") if part.strip()}

    sections = filter_sections(
        courses,
        include_types=include_types,
        section_codes=section_codes,
    )

    if not sections:
        print(
            "No matching sections with scheduled meeting times were found. "
            "Try different --sections or --types.",
            file=sys.stderr,
        )
        _print_sections(
            [s for course in courses for s in course.sections if not s.cancelled]
        )
        return 1

    _print_sections(sections)

    if args.dry_run:
        print(f"\nDry run: would write {len(sections)} section(s) to {args.output}")
        return 0

    write_calendar(sections, term, args.output)
    print(f"\nWrote {args.output}")
    print("\nTo add to Google Calendar:")
    print("  1. Open Google Calendar → Settings → Import & export → Import")
    print(f"  2. Select {args.output.resolve()}")
    print("  3. Choose which calendar to add events to")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
