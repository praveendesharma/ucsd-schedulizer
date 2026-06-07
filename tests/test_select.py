"""Tests for interactive section selection helpers."""

from ucsd_schedulizer.models import Course, MeetingTime, Section
from ucsd_schedulizer.select import (
    lecture_options,
    pick_one,
    related_sections,
    select_sections_for_course,
)


def _section(
    section_type: str,
    section_code: str,
    *,
    instructor: str = "Smith, Jane",
) -> Section:
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


def _course() -> Course:
    return Course(
        subject="MATH",
        number="20E",
        title="Vector Calculus",
        sections=[
            _section("LE", "A00", instructor="Alpha, Ann"),
            _section("DI", "A01", instructor="Alpha, Ann"),
            _section("LE", "B00", instructor="Beta, Bob"),
            _section("DI", "B01", instructor="Beta, Bob"),
        ],
    )


def test_lecture_options() -> None:
    assert len(lecture_options(_course())) == 2


def test_related_sections_match_lecture_prefix() -> None:
    course = _course()
    lecture = lecture_options(course)[0]
    related = related_sections(course, lecture, {"DI"})
    assert len(related) == 1
    assert related[0].section_code == "A01"


def test_pick_one_auto_selects_single_option() -> None:
    chosen = pick_one(["only"], label="Test", describe=str)
    assert chosen == "only"


def test_select_sections_for_course_picks_lecture_and_discussion() -> None:
    responses = iter(["2"])
    sections = select_sections_for_course(
        _course(),
        include_types={"LE", "DI"},
        input_fn=lambda _prompt: next(responses),
    )
    assert len(sections) == 2
    assert sections[0].section_code == "B00"
    assert sections[1].section_code == "B01"
