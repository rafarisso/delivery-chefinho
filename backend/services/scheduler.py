"""Scheduler helper utilities."""
from __future__ import annotations

from datetime import date, datetime, timedelta, time

import pytz


def week_bounds(week_end: date) -> tuple[date, date]:
    """Return the start and end dates for the business week."""

    week_start = week_end - timedelta(days=6)
    return week_start, week_end


def current_wednesday(now: datetime | None = None, tz: str = "America/Sao_Paulo") -> date:
    """Return the business week end (Wednesday) for the given datetime."""

    tzinfo = pytz.timezone(tz)
    now_localized = (now or datetime.utcnow()).astimezone(tzinfo)
    offset = (now_localized.weekday() - 2) % 7
    return now_localized.date() - timedelta(days=offset)


def next_wednesday_at(
    now: datetime | None = None,
    tz: str = "America/Sao_Paulo",
    hour: int = 9,
    minute: int = 0,
) -> datetime:
    """Return the next Wednesday at the given time in the configured timezone."""

    tzinfo = pytz.timezone(tz)
    now_local = (now or datetime.utcnow()).astimezone(tzinfo)
    days_ahead = (2 - now_local.weekday()) % 7
    candidate_date = now_local.date() + timedelta(days=days_ahead)
    target_naive = datetime.combine(candidate_date, time(hour=hour, minute=minute))
    target_local = tzinfo.localize(target_naive)

    if target_local <= now_local:
        next_date = candidate_date + timedelta(days=7)
        next_naive = datetime.combine(next_date, time(hour=hour, minute=minute))
        target_local = tzinfo.localize(next_naive)

    return target_local


def is_within_reminder_window(
    now: datetime | None = None,
    tz: str = "America/Sao_Paulo",
    hour: int = 9,
    minute: int = 0,
    tolerance_minutes: int = 15,
) -> bool:
    """Return whether now is within the reminder window around Wednesday at the configured time."""

    tzinfo = pytz.timezone(tz)
    now_local = (now or datetime.utcnow()).astimezone(tzinfo)
    target_date = current_wednesday(now_local, tz=tz)
    target_naive = datetime.combine(target_date, time(hour=hour, minute=minute))
    target_local = tzinfo.localize(target_naive)
    delta = abs((now_local - target_local).total_seconds())
    return delta <= tolerance_minutes * 60
