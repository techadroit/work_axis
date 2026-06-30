# Shim – re-exports from core so existing imports keep working unchanged.
from core.utils.time_util import (  # noqa: F401
    get_utc_time,
    get_current_timestamp_ms,
    get_current_timestamp_ns_datetime,
    utc_now_iso,
    parse_utc_iso,
)
