"""Build an ICS calendar file from class sections."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

from .models import Section, TermDates

PACIFIC = ZoneInfo("America/Los_Angeles")


def _minutes_to_time(minutes: int) -> tuple[int, int]:
    return divmod(minutes, 60)


def _first_date_on_or_after(start: date, weekday: int) -> date:
    delta = (weekday - start.weekday()) % 7
    return start + timedelta(days=delta)


def _section_events(section: Section, term: TermDates) -> list[Event]:
    if section.meeting is None:
        return []

    events: list[Event] = []
    for weekday in section.meeting.days:
        event_date = _first_date_on_or_after(term.start, weekday)
        start_hour, start_minute = _minutes_to_time(section.meeting.start_minutes)
        end_hour, end_minute = _minutes_to_time(section.meeting.end_minutes)

        start_dt = datetime(
            event_date.year,
            event_date.month,
            event_date.day,
            start_hour,
            start_minute,
            tzinfo=PACIFIC,
        )
        end_dt = datetime(
            event_date.year,
            event_date.month,
            event_date.day,
            end_hour,
            end_minute,
            tzinfo=PACIFIC,
        )

        location_parts = [part for part in (section.building, section.room) if part]
        location = " ".join(location_parts)

        summary = f"{section.course_code} {section.section_type} {section.section_code}"
        description_lines = [
            section.course_title,
            f"Type: {section.section_type}",
            f"Section: {section.section_code}",
        ]
        if section.instructor:
            description_lines.append(f"Instructor: {section.instructor}")
        if section.section_id:
            description_lines.append(f"Section ID: {section.section_id}")

        event = Event()
        event.add("summary", summary)
        event.add("description", "\n".join(description_lines))
        if location:
            event.add("location", location)
        event.add("dtstart", start_dt)
        event.add("dtend", end_dt)
        event.add("rrule", {"freq": "weekly", "until": term.end})
        events.append(event)

    return events


def build_calendar(sections: list[Section], term: TermDates) -> Calendar:
    cal = Calendar()
    cal.add("prodid", "-//UCSD Schedulizer//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", f"UCSD {term.name}")
    cal.add("x-wr-timezone", "America/Los_Angeles")

    for section in sections:
        for event in _section_events(section, term):
            cal.add_component(event)

    return cal


def write_calendar(sections: list[Section], term: TermDates, output: Path) -> None:
    cal = build_calendar(sections, term)
    output.write_bytes(cal.to_ical())
