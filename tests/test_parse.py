"""Tests for parsing helpers."""

from datetime import date

from ucsd_schedulizer.parse import parse_days, parse_time_range
from ucsd_schedulizer.terms import parse_term


def test_parse_term_code() -> None:
    term = parse_term("SP26")
    assert term.code == "SP26"
    assert term.start == date(2026, 3, 30)


def test_parse_term_name() -> None:
    term = parse_term("Spring Quarter 2026")
    assert term.code == "SP26"


def test_parse_days_mwf() -> None:
    assert parse_days("MWF") == (0, 2, 4)


def test_parse_days_tuth() -> None:
    assert parse_days("TuTh") == (1, 3)


def test_parse_time_range() -> None:
    start, end = parse_time_range("1:00p-1:50p")
    assert start == 13 * 60
    assert end == 13 * 60 + 50
