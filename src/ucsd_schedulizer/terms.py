"""Map human-readable quarter names to UCSD term codes and instruction dates."""

from __future__ import annotations

import re
from datetime import date

from .models import TermDates

# Instruction dates from the UCSD academic calendar.
# https://students.ucsd.edu/calendar/academic/2025-26.html
_TERM_DATES: dict[str, TermDates] = {
    "FA25": TermDates("Fall Quarter 2025", "FA25", date(2025, 9, 25), date(2025, 12, 12)),
    "WI26": TermDates("Winter Quarter 2026", "WI26", date(2026, 1, 5), date(2026, 3, 20)),
    "SP26": TermDates("Spring Quarter 2026", "SP26", date(2026, 3, 30), date(2026, 6, 12)),
    "S126": TermDates("Summer Session I 2026", "S126", date(2026, 6, 29), date(2026, 7, 31)),
    "S226": TermDates("Summer Session II 2026", "S226", date(2026, 8, 3), date(2026, 9, 4)),
    "FA24": TermDates("Fall Quarter 2024", "FA24", date(2024, 9, 26), date(2024, 12, 13)),
    "WI25": TermDates("Winter Quarter 2025", "WI25", date(2025, 1, 6), date(2025, 3, 21)),
    "SP25": TermDates("Spring Quarter 2025", "SP25", date(2025, 3, 31), date(2025, 6, 13)),
}

_SEASON_CODES = {
    "fall": "FA",
    "winter": "WI",
    "spring": "SP",
    "summer": "S1",
}

_CODE_RE = re.compile(r"^(FA|WI|SP|S[123]|SU|SA)\d{2}$", re.IGNORECASE)
_NAME_RE = re.compile(
    r"(?P<season>fall|winter|spring|summer)\s*(?:quarter|session)?\s*"
    r"(?P<year>20\d{2}|\d{2})",
    re.IGNORECASE,
)


def parse_term(raw: str) -> TermDates:
    """Convert a term code or name like ``SP26`` or ``Spring Quarter 2026``."""
    text = raw.strip()
    code_match = _CODE_RE.match(text.replace(" ", ""))
    if code_match:
        code = code_match.group(0).upper()
        if code in _TERM_DATES:
            return _TERM_DATES[code]
        raise ValueError(
            f"Unknown term code {code!r}. Known codes: {', '.join(sorted(_TERM_DATES))}"
        )

    name_match = _NAME_RE.search(text)
    if name_match:
        season = name_match.group("season").lower()
        year_text = name_match.group("year")
        year = int(year_text) if len(year_text) == 4 else 2000 + int(year_text)
        prefix = _SEASON_CODES[season]
        code = f"{prefix}{year % 100:02d}"
        if code in _TERM_DATES:
            return _TERM_DATES[code]
        raise ValueError(
            f"No instruction dates on file for {text!r} ({code}). "
            f"Known terms: {', '.join(d.name for d in _TERM_DATES.values())}"
        )

    raise ValueError(
        f"Could not parse quarter {raw!r}. "
        "Use a term code (e.g. SP26) or name (e.g. 'Spring Quarter 2026')."
    )


def list_terms() -> list[TermDates]:
    return list(_TERM_DATES.values())
