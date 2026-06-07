"""Data models for scraped schedule information."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class MeetingTime:
    """Weekly meeting time for a class section."""

    days: tuple[int, ...]  # 0=Mon .. 6=Sun (Python weekday convention)
    start_minutes: int  # minutes since midnight
    end_minutes: int


@dataclass(frozen=True)
class Section:
    """A single scheduled component (lecture, discussion, lab, etc.)."""

    course_code: str  # e.g. "DSC 190"
    course_title: str
    section_type: str  # LE, DI, LA, etc.
    section_code: str  # e.g. A00
    section_id: str | None
    meeting: MeetingTime | None
    building: str | None
    room: str | None
    instructor: str | None
    cancelled: bool = False


@dataclass
class Course:
    """A course with one or more sections."""

    subject: str
    number: str
    title: str
    sections: list[Section] = field(default_factory=list)

    @property
    def code(self) -> str:
        return f"{self.subject} {self.number}"


@dataclass(frozen=True)
class TermDates:
    """First and last day of instruction for a quarter."""

    name: str
    code: str
    start: date
    end: date
