"""Parse UCSD Schedule of Classes HTML into structured course data."""

from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from .models import Course, MeetingTime, Section

DAY_MAP = {
    "M": 0,
    "Tu": 1,
    "T": 1,
    "W": 2,
    "Th": 3,
    "R": 3,
    "F": 4,
    "S": 5,
    "Su": 6,
    "Sun": 6,
}

_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})([ap])-(\d{1,2}):(\d{2})([ap])$", re.IGNORECASE)
_DAYS_RE = re.compile(r"Sun|Tu|[MWFS]|Th")
_SUBJECT_RE = re.compile(r"^(.+) \(([A-Z& ]+?) ?\)$")
_SECTION_TYPES = {"LE", "DI", "LA", "SE", "CL", "PR", "CO", "FW", "IN", "MT"}


def _parse_time_minutes(hour: int, minute: int, ampm: str) -> int:
    am = ampm.lower() == "a"
    if hour == 12:
        hour = 0 if am else 12
    elif not am:
        hour += 12
    return hour * 60 + minute


def parse_time_range(text: str) -> tuple[int, int]:
    match = _TIME_RE.match(text.strip())
    if not match:
        raise ValueError(f"Invalid time range: {text!r}")
    h1, m1, ap1, h2, m2, ap2 = match.groups()
    start = _parse_time_minutes(int(h1), int(m1), ap1)
    end = _parse_time_minutes(int(h2), int(m2), ap2)
    return start, end


def parse_days(text: str) -> tuple[int, ...]:
    if text.strip().upper() == "TBA":
        return ()
    days = []
    for token in _DAYS_RE.findall(text):
        key = "Tu" if token == "T" else token
        days.append(DAY_MAP[key])
    return tuple(sorted(set(days)))


def _normalize_tds(row: Tag) -> list[str]:
    """Normalize section row cells to a fixed 13-column layout."""
    tds = [cell.get_text(strip=True) for cell in row.find_all("td")]
    if row.get("class") == ["nonenrtxt"]:
        return tds

    if len(tds) == 10:
        tds = tds[:6] + ["TBA", "TBA", "TBA"] + tds[6:]
    elif len(tds) == 6:
        return tds
    elif len(tds) != 13:
        return tds
    return tds


def parse_schedule_html(html: str) -> list[Course]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.tbrdr")
    if table is None:
        return []

    courses: list[Course] = []
    subject = ""
    current: Course | None = None

    for row in table.find_all("tr"):
        classes = row.get("class") or []

        subject_heading = row.find("h2")
        if subject_heading:
            heading = " ".join(subject_heading.get_text(" ", strip=True).split())
            match = _SUBJECT_RE.match(heading)
            if match:
                subject = match.group(2).strip()
            continue

        if row.find(class_="crsheader") and len(row.find_all("td")) == 4:
            cells = row.find_all("td")
            number = cells[1].get_text(strip=True)
            title_link = cells[2].find("a")
            title = title_link.get_text(strip=True) if title_link else cells[2].get_text(strip=True)
            title = re.sub(r"\(\s*\d+\s*Units\s*\)$", "", title).strip()
            if current and current.sections:
                courses.append(current)
            current = Course(subject=subject, number=number, title=title)
            continue

        if "sectxt" not in classes:
            continue

        tds = _normalize_tds(row)
        if len(tds) == 6:
            _, _, section_id, meeting_type, section_code, days = (tds + ["", ""])[:6]
            time_text = ""
            building = None
            room = None
            instructor = None
        elif len(tds) >= 13:
            _, _, section_id, meeting_type, section_code, days, time_text, building, room, instructor, *_rest = (
                tds + [""] * 13
            )[:13]
        else:
            continue

        if meeting_type not in _SECTION_TYPES:
            continue
        if current is None or not subject:
            continue

        cancelled = days.lower() == "cancelled"
        meeting: MeetingTime | None = None
        if not cancelled and days.upper() != "TBA" and _TIME_RE.match(time_text or ""):
            day_tuple = parse_days(days)
            if day_tuple:
                start, end = parse_time_range(time_text)
                meeting = MeetingTime(days=day_tuple, start_minutes=start, end_minutes=end)

        if building == "TBA":
            building = None
        if room == "TBA":
            room = None

        current.sections.append(
            Section(
                course_code=f"{subject} {current.number}".strip(),
                course_title=current.title,
                section_type=meeting_type,
                section_code=section_code,
                section_id=section_id or None,
                meeting=meeting,
                building=building,
                room=room,
                instructor=instructor or None,
                cancelled=cancelled,
            )
        )

    if current and current.sections:
        courses.append(current)

    return courses


def normalize_course_query(text: str) -> str:
    """Turn ``dsc190`` or ``DSC-190`` into ``DSC 190``."""
    text = text.strip().upper().replace("-", " ")
    match = re.match(r"^([A-Z&]+)\s*(\d+[A-Z]*)$", text.replace(" ", ""))
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return text


def parse_course_list(raw: str) -> list[str]:
    parts = re.split(r"[,;\n]+", raw)
    return [normalize_course_query(part) for part in parts if part.strip()]


def filter_sections(
    courses: Iterable[Course],
    *,
    include_types: set[str] | None = None,
    section_codes: set[str] | None = None,
) -> list[Section]:
    selected: list[Section] = []
    for course in courses:
        for section in course.sections:
            if section.cancelled or section.meeting is None:
                continue
            if include_types and section.section_type not in include_types:
                continue
            if section_codes and section.section_code not in section_codes:
                continue
            selected.append(section)
    return selected
