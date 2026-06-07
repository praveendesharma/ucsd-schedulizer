"""Tests for HTML schedule parsing."""

from pathlib import Path

from ucsd_schedulizer.parse import parse_schedule_html

FIXTURE = Path(__file__).parent / "fixtures" / "sp26_sample.html"


def test_parse_fixture_has_sections() -> None:
    html = FIXTURE.read_text()
    courses = parse_schedule_html(html)
    assert len(courses) >= 1
    dsc = next(c for c in courses if c.number == "190")
    assert dsc.subject == "DSC"
    assert dsc.title.startswith("Topics in Data Science")
    lectures = [s for s in dsc.sections if s.section_type == "LE" and s.section_code == "A00"]
    assert len(lectures) == 1
    assert lectures[0].meeting is not None
    assert lectures[0].building == "CENTR"
    assert lectures[0].room == "201"
