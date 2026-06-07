"""Format and group class sections for interactive selection."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from .models import Course, Section

T = TypeVar("T")

DAY_NAMES = ("M", "Tu", "W", "Th", "F", "S", "Su")


def format_meeting(section: Section) -> str:
    if section.meeting is None:
        return "TBA"
    days = "".join(DAY_NAMES[d] for d in section.meeting.days)
    sh, sm = divmod(section.meeting.start_minutes, 60)
    eh, em = divmod(section.meeting.end_minutes, 60)
    return f"{days} {sh}:{sm:02d}-{eh}:{em:02d}"


def format_location(section: Section) -> str:
    return " ".join(part for part in (section.building, section.room) if part) or "TBA"


def format_section(section: Section) -> str:
    instructor = section.instructor or "Staff"
    return (
        f"{section.section_type} {section.section_code} — "
        f"{format_meeting(section)}, {format_location(section)}, {instructor}"
    )


def format_section_brief(section: Section) -> str:
    return (
        f"{section.section_type} {section.section_code} — "
        f"{format_meeting(section)}, {format_location(section)}"
    )


def _section_prefix(section_code: str) -> str:
    return section_code[0] if section_code else ""


def active_sections(course: Course, include_types: set[str]) -> list[Section]:
    return [
        section
        for section in course.sections
        if not section.cancelled
        and section.meeting is not None
        and section.section_type in include_types
    ]


def lecture_options(course: Course) -> list[Section]:
    return [s for s in active_sections(course, {"LE"})]


def related_sections(course: Course, lecture: Section, include_types: set[str]) -> list[Section]:
    prefix = _section_prefix(lecture.section_code)
    return [
        section
        for section in active_sections(course, include_types)
        if section.section_type != "LE" and _section_prefix(section.section_code) == prefix
    ]


def pick_one(
    options: list[T],
    *,
    label: str,
    describe: Callable[[T], str],
    input_fn: Callable[[str], str] = input,
    auto_first: bool = False,
) -> T:
    if not options:
        raise ValueError(f"No options available for {label}")
    if len(options) == 1:
        chosen = options[0]
        print(f"{label}: {describe(chosen)}")
        return chosen

    if auto_first:
        chosen = options[0]
        print(f"{label}: {describe(chosen)} (auto-selected)")
        return chosen

    print(f"\n{label}")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {describe(option)}")

    while True:
        response = input_fn(f"Choose 1-{len(options)}: ").strip()
        if response.isdigit():
            choice = int(response)
            if 1 <= choice <= len(options):
                return options[choice - 1]
        print(f"Enter a number between 1 and {len(options)}.")


def select_sections_for_course(
    course: Course,
    *,
    include_types: set[str],
    input_fn: Callable[[str], str] = input,
    auto_first: bool = False,
) -> list[Section]:
    """Pick lecture and related sections for one course."""
    lectures = lecture_options(course)
    if not lectures:
        print(f"No scheduled lectures found for {course.code}. Skipping.")
        return []

    lecture = pick_one(
        lectures,
        label=f"{course.code} — choose a lecture",
        describe=format_section,
        input_fn=input_fn,
        auto_first=auto_first,
    )

    selected = [lecture]
    for section_type in ("DI", "LA"):
        if section_type not in include_types:
            continue
        options = [s for s in related_sections(course, lecture, {section_type})]
        if not options:
            continue
        chosen = pick_one(
            options,
            label=f"{course.code} — choose a {section_type.lower()} section",
            describe=format_section,
            input_fn=input_fn,
            auto_first=auto_first,
        )
        selected.append(chosen)

    return selected


def select_schedule(
    courses: list[Course],
    requested: list[str],
    *,
    include_types: set[str],
    input_fn: Callable[[str], str] = input,
    auto_first: bool = False,
) -> list[Section]:
    """Interactively pick sections for each requested course."""
    by_code = {course.code.upper(): course for course in courses}
    selected: list[Section] = []

    for course_code in requested:
        course = by_code.get(course_code.upper())
        if course is None:
            close = [code for code in by_code if course_code.upper() in code]
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            print(f"Warning: {course_code} not found in schedule.{hint}")
            continue
        selected.extend(
            select_sections_for_course(
                course,
                include_types=include_types,
                input_fn=input_fn,
                auto_first=auto_first,
            )
        )

    return selected


def sections_by_professor(
    course: Course,
    include_types: set[str],
) -> list[tuple[str, list[Section]]]:
    """Group a course's sections by lecture professor."""
    groups: list[tuple[str, list[Section]]] = []
    for lecture in lecture_options(course):
        instructor = lecture.instructor or "Staff"
        sections = [lecture]
        for section_type in ("DI", "LA"):
            if section_type in include_types:
                sections.extend(related_sections(course, lecture, {section_type}))
        groups.append((instructor, sections))
    return groups


def print_sections_by_professor(
    courses: list[Course],
    requested: list[str],
    *,
    include_types: set[str],
) -> None:
    """Print all sections for each course, grouped by professor."""
    by_code = {course.code.upper(): course for course in courses}

    for course_code in requested:
        course = by_code.get(course_code.upper())
        if course is None:
            close = [code for code in by_code if course_code.upper() in code]
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            print(f"\n{course_code} — not found.{hint}\n")
            continue

        print(f"\n{course.code} — {course.title}")
        groups = sections_by_professor(course, include_types)
        if not groups:
            print("  No scheduled sections found.")
            continue

        for instructor, sections in groups:
            lecture = sections[0]
            print(f"\n  {instructor} ({lecture.section_type} {lecture.section_code})")
            for section in sections:
                print(f"    {format_section_brief(section)}")
