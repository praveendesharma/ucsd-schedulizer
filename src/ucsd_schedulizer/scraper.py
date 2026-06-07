"""Fetch course schedules from UCSD Schedule of Classes."""

from __future__ import annotations

import urllib.parse

import httpx

from .models import Course
from .parse import parse_course_list, parse_schedule_html

BASE_URL = "https://act.ucsd.edu/scheduleOfClasses/scheduleOfClassesStudentResult.htm"


def build_search_url(term_code: str, courses: list[str]) -> str:
    course_query = ", ".join(courses)
    params = {
        "selectedTerm": term_code,
        "tabNum": "tabs-crs",
        "courses": course_query,
        "page": "1",
    }
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"


def fetch_schedule(term_code: str, courses: str | list[str]) -> list[Course]:
    """Fetch and parse schedules for the given term and course list."""
    course_list = parse_course_list(courses) if isinstance(courses, str) else courses
    if not course_list:
        raise ValueError("Provide at least one course code, e.g. 'DSC 190, CSE 100'.")

    url = build_search_url(term_code, course_list)
    response = httpx.get(url, timeout=30.0, follow_redirects=True)
    response.raise_for_status()

    parsed = parse_schedule_html(response.text)
    if not parsed:
        raise RuntimeError(
            f"No courses found for {', '.join(course_list)} in term {term_code}. "
            "Check the quarter code and course numbers."
        )
    return parsed
