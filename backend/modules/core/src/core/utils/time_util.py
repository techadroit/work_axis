import datetime
from datetime import datetime, timezone


def get_utc_time() -> str:
    time = utc_now_iso()
    return time


def get_current_timestamp_ms() -> int:
    """
    Get current timestamp in milliseconds.

    Returns:
        int: Current UTC timestamp in milliseconds.
    """
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def get_current_timestamp_ns_datetime() -> int:
    """
    Get current timestamp in nanoseconds using datetime.

    Returns:
        int: Current UTC timestamp in nanoseconds.
    """
    dt = datetime.now(timezone.utc)
    return int(dt.timestamp() * 1_000_000_000)


def utc_now_iso() -> str:
    # Produce "...Z" (UTC) with milliseconds
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_utc_iso(s: str) -> datetime:
    # Accept "Z" and "+00:00" formats; return aware UTC datetime
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include timezone (e.g., 'Z').")
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
