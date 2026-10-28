"""Time: timestamps, spans, zones and durations."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

from ..schema import Field, Module, error, kv, listout, note, opts, value

try:  # Windows ships without a tz database; tzdata is a pip dependency.
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones
except ImportError:  # pragma: no cover - Python < 3.9
    ZoneInfo = None  # type: ignore[assignment]
    ZoneInfoNotFoundError = Exception  # type: ignore[misc,assignment]
    available_timezones = lambda: set()  # type: ignore[assignment]

COMMON_ZONES = [
    "UTC",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Madrid",
    "Europe/Rome",
    "Europe/Amsterdam",
    "Europe/Lisbon",
    "Europe/Stockholm",
    "Europe/Warsaw",
    "Europe/Athens",
    "Europe/Istanbul",
    "Europe/Moscow",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "America/Mexico_City",
    "America/Sao_Paulo",
    "America/Argentina/Buenos_Aires",
    "Asia/Dubai",
    "Asia/Karachi",
    "Asia/Kolkata",
    "Asia/Bangkok",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Singapore",
    "Asia/Tokyo",
    "Asia/Seoul",
    "Australia/Perth",
    "Australia/Sydney",
    "Pacific/Auckland",
    "Africa/Cairo",
    "Africa/Lagos",
    "Africa/Johannesburg",
]

DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%Y/%m/%d %H:%M",
    "%Y/%m/%d",
    "%d.%m.%Y %H:%M",
    "%d.%m.%Y",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%d %b %Y",
    "%b %d, %Y",
    "%B %d, %Y",
)

RELATIVE = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*(s|sec|secs|seconds?|m|min|mins|minutes?|h|hr|hrs|hours?|d|day|days|w|week|weeks|mo|month|months?|y|yr|years?)\s*$", re.I)
DURATION_PART = re.compile(r"(\d+(?:\.\d+)?)\s*(y|yr|years?|mo|months?|w|weeks?|d|days?|h|hrs?|hours?|m|mins?|minutes?|s|secs?|seconds?)\b", re.I)

UNIT_SECONDS = {
    "s": 1,
    "sec": 1,
    "secs": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,
    "min": 60,
    "mins": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "hour": 3600,
    "hours": 3600,
    "d": 86400,
    "day": 86400,
    "days": 86400,
    "w": 604800,
    "week": 604800,
    "weeks": 604800,
    "mo": 2629800,
    "month": 2629800,
    "months": 2629800,
    "y": 31557600,
    "yr": 31557600,
    "year": 31557600,
    "years": 31557600,
}


def parse_datetime(raw: str, *, tz=None) -> datetime:
    """Parse ISO-ish input, 'now'/'today', or a relative offset like +3d."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("empty date")
    low = s.lower()
    base = datetime.now(tz) if tz is not None else datetime.now()
    if low in ("now", "right now"):
        return base
    if low == "today":
        return base.replace(hour=0, minute=0, second=0, microsecond=0)
    if low == "tomorrow":
        return base.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if low == "yesterday":
        return base.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    rel = RELATIVE.match(s)
    if rel:
        amount = float(rel.group(1))
        unit = rel.group(2).lower().rstrip("s")
        seconds = UNIT_SECONDS.get(unit + "s", UNIT_SECONDS.get(unit))
        if seconds is None:
            raise ValueError("unknown unit")
        return base + timedelta(seconds=amount * seconds)
    iso = s.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(iso)
        if parsed.tzinfo is None and tz is not None:
            parsed = parsed.replace(tzinfo=tz)
        return parsed
    except ValueError:
        pass
    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(s, fmt)
            return parsed.replace(tzinfo=tz) if tz is not None else parsed
        except ValueError:
            continue
    raise ValueError(f"can't read “{s}”")


def parse_duration(raw: str) -> float:
    """'1h 30m' -> 5400.0 seconds. Bare numbers are seconds."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("empty duration")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", s):
        return float(s)
    total = 0.0
    found = False
    for value_str, unit in DURATION_PART.findall(s):
        key = unit.lower()
        seconds = UNIT_SECONDS.get(key) or UNIT_SECONDS.get(key.rstrip("s"))
        if seconds is None:
            continue
        total += float(value_str) * seconds
        found = True
    if not found:
        raise ValueError(f"can't read “{s}” as a duration")
    return total


def human_delta(seconds: float) -> str:
    future = seconds >= 0
    seconds = abs(seconds)
    parts: list[str] = []
    for label, size in (("year", 31557600), ("month", 2629800), ("day", 86400), ("hour", 3600), ("minute", 60)):
        if seconds >= size:
            count = int(seconds // size)
            seconds -= count * size
            parts.append(f"{count} {label}{'s' if count != 1 else ''}")
        if len(parts) == 2:
            break
    if not parts:
        parts.append(f"{int(seconds)} second{'s' if int(seconds) != 1 else ''}")
    return ("in " if future else "") + " ".join(parts) + ("" if future else " ago")


def _local_zone_name() -> str:
    try:
        name = datetime.now().astimezone().tzinfo
        key = getattr(name, "key", None)
        return key or (name.tzname(None) if name else "local")  # type: ignore[union-attr]
    except Exception:
        return "local"


def _zone(name: str):
    if name == "local":
        return datetime.now().astimezone().tzinfo
    if ZoneInfo is None:
        raise ValueError("time zone support is unavailable")
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, KeyError, ValueError):
        raise ValueError(f"unknown zone “{name}”")


def _zone_options(extra: str | None = None) -> tuple[dict[str, str], ...]:
    names = ["local", *COMMON_ZONES]
    if extra and extra not in names:
        names.append(extra)
    return tuple({"value": n, "label": "Local time" if n == "local" else n} for n in names)


class Timestamp(Module):
    id = "timestamp"
    category = "time"
    title = "Timestamp ⇄ Date"
    subtitle = "Epoch, ISO and local, both ways"
    icon = "clock"
    keywords = ("timestamp", "epoch", "unix", "iso", "8601", "date", "utc", "convert", "milliseconds")
    fields = (
        Field(
            "input",
            "text",
            "Timestamp or date",
            default="now",
            placeholder="1735689600, 2026-01-01T00:00:00Z, now, +2d",
            hint="Accepts epoch seconds/millis, ISO 8601, “now” or offsets like +3h",
            mono=True,
        ),
        Field(
            "unit",
            "select",
            "Epoch unit",
            default="auto",
            options=opts(("auto", "Detect"), ("s", "Seconds"), ("ms", "Milliseconds")),
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        raw = str(v["input"]).strip()
        if not raw:
            return [note("Type an epoch value, an ISO date, “now” or “+2d”.")]
        try:
            if re.fullmatch(r"-?\d+(?:\.\d+)?", raw):
                numeric = float(raw)
                unit = v["unit"]
                if unit == "auto":
                    unit = "ms" if abs(numeric) >= 1e11 else "s"
                seconds = numeric / 1000.0 if unit == "ms" else numeric
                dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
            else:
                dt = parse_datetime(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                seconds = dt.timestamp()
        except (ValueError, OverflowError, OSError) as exc:
            return [error(f"{exc}" if str(exc) else "That value can't be read as a date.")]
        local = dt.astimezone()
        epoch_s = int(seconds)
        epoch_ms = int(round(seconds * 1000))
        week = dt.isocalendar()
        current = datetime.now(tz=timezone.utc).timestamp()
        return [
            value("ISO 8601", dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt.tzinfo == timezone.utc else dt.isoformat()),
            kv(
                "Readings",
                [
                    ("Unix (s)", f"{epoch_s:,}"),
                    ("Unix (ms)", f"{epoch_ms:,}"),
                    ("UTC", dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
                    ("Local", local.strftime("%Y-%m-%d %H:%M:%S %Z")),
                    ("Weekday", dt.strftime("%A")),
                    ("Week", f"{week.year}-W{week.week:02d}"),
                ],
            ),
            listout(
                "Relative",
                [
                    human_delta(seconds - current),
                    f"day {dt.timetuple().tm_yday} of {dt.year}",
                    f"{(dt - dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)).days} days into the year",
                ],
            ),
        ]


class DateDifference(Module):
    id = "datediff"
    category = "time"
    title = "Date Difference"
    subtitle = "Days, weeks, business days"
    icon = "calendar"
    keywords = ("date", "difference", "between", "days", "duration", "age", "business days", "workdays")
    fields = (
        Field("start", "text", "Start", default="today", hint="YYYY-MM-DD, today, or -7d", mono=True),
        Field("end", "text", "End", default="+30d", hint="YYYY-MM-DD, today, or +30d", mono=True),
        Field("inclusive", "toggle", "Include both end days", default=False),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            start = parse_datetime(str(v["start"]))
            end = parse_datetime(str(v["end"]))
        except ValueError as exc:
            return [error(str(exc))]
        swapped = end < start
        if swapped:
            start, end = end, start
        span = end - start
        days = span.days
        adjusted = days + (1 if v["inclusive"] else 0)
        business = 0
        cursor = start.date()
        while cursor < end.date():
            if cursor.weekday() < 5:
                business += 1
            cursor += timedelta(days=1)
        if v["inclusive"] and end.date().weekday() < 5:
            business += 1
        total_seconds = span.total_seconds()
        years = days / 365.25
        outputs = [
            value("Days", f"{adjusted:,}"),
            kv(
                "Span",
                [
                    ("Weeks", f"{adjusted // 7} weeks {adjusted % 7} days"),
                    ("Business days", f"{business:,}"),
                    ("Hours", f"{total_seconds / 3600:,.2f}"),
                    ("Minutes", f"{total_seconds / 60:,.0f}"),
                    ("Months (avg)", f"{days / 30.4375:,.2f}"),
                    ("Years (avg)", f"{years:,.2f}"),
                ],
            ),
            kv("Range", [("From", start.strftime("%a %d %b %Y")), ("To", end.strftime("%a %d %b %Y"))]),
            listout("Readable", [human_delta(total_seconds), f"exactly {days:,} × 24 h"] ),
        ]
        if swapped:
            outputs.append(note("The dates were swapped so the span stays positive."))
        return outputs


class TimeZones(Module):
    id = "timezone"
    category = "time"
    title = "Time Zones"
    subtitle = "Move a moment between zones"
    icon = "globe"
    keywords = ("timezone", "zone", "utc", "gmt", "conversion", "abroad", "meeting", "local time", "offset")
    fields = (
        Field("when", "text", "Date & time", default="now", hint="ISO, now, or today 15:30", mono=True),
        Field("from_zone", "select", "From", default="local", options=_zone_options()),
        Field("to_zone", "select", "To", default="Asia/Tokyo", options=_zone_options()),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            src = _zone(v["from_zone"])
            dst = _zone(v["to_zone"])
        except ValueError as exc:
            return [error(str(exc))]
        try:
            dt = parse_datetime(str(v["when"]), tz=src)
        except ValueError as exc:
            return [error(str(exc))]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=src)
        converted = dt.astimezone(dst)
        diff = (converted.utcoffset() or timedelta()) - (dt.utcoffset() or timedelta())
        hours = diff.total_seconds() / 3600.0
        return [
            value("There", converted.strftime("%a %d %b, %H:%M")),
            kv(
                "Details",
                [
                    ("Here", dt.strftime("%a %d %b, %H:%M %Z")),
                    ("There", converted.strftime("%Y-%m-%d %H:%M %Z")),
                    ("Difference", f"{hours:+.1f} h"),
                    ("UTC", converted.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")),
                ],
            ),
            note("Offsets come from the zone database, so daylight saving is included."),
        ]


class Countdown(Module):
    id = "countdown"
    category = "time"
    title = "Countdown & Duration"
    subtitle = "Time left, or a duration in parts"
    icon = "hourglass"
    keywords = ("countdown", "duration", "remaining", "timer", "time left", "how long", "since", "until")
    fields = (
        Field(
            "mode",
            "select",
            "Mode",
            default="until",
            options=opts(("until", "Time until a date"), ("duration", "Break down a duration")),
        ),
        Field(
            "target",
            "text",
            "Target date",
            default="+7d",
            hint="YYYY-MM-DD HH:MM, +7d, or a date like 25 Dec 2026",
            mono=True,
            visible_when={"key": "mode", "in": ["until"]},
        ),
        Field(
            "duration",
            "text",
            "Duration",
            default="1h 30m",
            placeholder="2d 4h 30m 15s",
            mono=True,
            visible_when={"key": "mode", "in": ["duration"]},
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        if v["mode"] == "duration":
            try:
                seconds = parse_duration(str(v["duration"]))
            except ValueError as exc:
                return [error(str(exc))]
            return _breakdown(seconds, "Duration")
        try:
            target = parse_datetime(str(v["target"]))
        except ValueError as exc:
            return [error(str(exc))]
        if target.tzinfo is None:
            target = target.replace(tzinfo=datetime.now().astimezone().tzinfo)
        seconds = (target - datetime.now(tz=target.tzinfo)).total_seconds()
        label = "Time left" if seconds >= 0 else "Time since"
        return [value("Countdown", human_delta(seconds)), *_breakdown(abs(seconds), label)]


def _breakdown(seconds: float, label: str) -> list[dict[str, Any]]:
    total = int(round(abs(seconds)))
    days, rest = divmod(total, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, secs = divmod(rest, 60)
    weeks, days = divmod(days, 7)
    return [
        kv(
            label,
            [
                ("Weeks", f"{weeks:,}"),
                ("Days", f"{days:,}"),
                ("Hours", f"{hours:,}"),
                ("Minutes", f"{minutes:,}"),
                ("Seconds", f"{secs:,}"),
            ],
        ),
        kv(
            "Totals",
            [
                ("Total days", f"{total / 86400:,.4f}"),
                ("Total hours", f"{total / 3600:,.3f}"),
                ("Total minutes", f"{total / 60:,.1f}"),
                ("Total seconds", f"{total:,}"),
            ],
        ),
        listout("Written", [f"{weeks}w {days}d {hours}h {minutes}m {secs}s"]),
    ]
