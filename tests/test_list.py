"""Tests for listing sections by professor."""

from ucsd_schedulizer.models import Course, MeetingTime, Section
from ucsd_schedulizer.select import sections_by_professor


def _course() -> Course:
    def section(section_type: str, section_code: str, instructor: str) -> Section:
        return Section(
            course_code="MATH 20E",
            course_title="Vector Calculus",
            section_type=section_type,
            section_code=section_code,
            section_id=None,
            meeting=MeetingTime(days=(0, 2, 4), start_minutes=600, end_minutes=650),
            building="WLH",
            room="2111",
            instructor=instructor,
        )

    return Course(
        subject="MATH",
        number="20E",
        title="Vector Calculus",
        sections=[
            section("LE", "A00", "Alpha, Ann"),
            section("DI", "A01", "Alpha, Ann"),
            section("LE", "B00", "Beta, Bob"),
            section("DI", "B01", "Beta, Bob"),
        ],
    )


def test_sections_by_professor_groups_lectures() -> None:
    groups = sections_by_professor(_course(), {"LE", "DI"})
    assert len(groups) == 2
    assert groups[0][0] == "Alpha, Ann"
    assert [s.section_code for s in groups[0][1]] == ["A00", "A01"]
    assert groups[1][0] == "Beta, Bob"
    assert [s.section_code for s in groups[1][1]] == ["B00", "B01"]
