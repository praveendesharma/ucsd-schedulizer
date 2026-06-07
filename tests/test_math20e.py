"""Tests for MATH 20E SP26 schedule parsing."""

from pathlib import Path

from ucsd_schedulizer.parse import merge_courses, parse_schedule_html
from ucsd_schedulizer.select import lecture_options

FIXTURE = Path(__file__).parent / "fixtures" / "math20e_sp26.html"


def test_math20e_sp26_merges_lectures_from_live_fixture() -> None:
    html = FIXTURE.read_text()
    courses = merge_courses(parse_schedule_html(html))
    math20e = next(c for c in courses if c.code == "MATH 20E")

    lectures = lecture_options(math20e)
    assert len(lectures) == 2

    by_section = {lecture.section_code: lecture for lecture in lectures}
    assert by_section["A00"].instructor == "Bach, Quang Tran"
    assert by_section["A00"].building == "PETER"
    assert by_section["B00"].instructor == "Ho, Sheng-Yang"
    assert by_section["B00"].building == "CENTR"
