import asyncio
import threading

from loguru import logger


class LogBroadcaster:
    """Loguru sink that broadcasts log records to all active SSE subscribers."""

    def __init__(self):
        self._subscribers: list[tuple[asyncio.Queue, asyncio.AbstractEventLoop]] = []
        self._lock = threading.Lock()

    def subscribe(self) -> asyncio.Queue:
        """Register a new SSE client and return its dedicated queue.
        Must be called from within a running asyncio event loop."""
        q: asyncio.Queue = asyncio.Queue(maxsize=500)
        loop = asyncio.get_running_loop()
        with self._lock:
            self._subscribers.append((q, loop))
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        """Remove a subscriber queue (called when the SSE client disconnects)."""
        with self._lock:
            self._subscribers = [(sq, lp) for sq, lp in self._subscribers if sq is not q]

    # ------------------------------------------------------------------
    # Loguru sink – called from any thread for every log record
    # ------------------------------------------------------------------
    def sink(self, message) -> None:
        record = message.record
        log_entry = {
            "time": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "level": record["level"].name,
            "message": record["message"],
            "name": record["name"],
            "function": record["function"],
            "line": record["line"],
        }
        with self._lock:
            subscribers = list(self._subscribers)

        for q, loop in subscribers:
            try:
                # Schedule the put on the owning event loop (thread-safe)
                loop.call_soon_threadsafe(q.put_nowait, log_entry)
            except Exception:
                pass  # queue full or loop closed – silently drop


log_broadcaster = LogBroadcaster()
# Register as an additional loguru sink (keeps the default stderr sink intact)
logger.add(log_broadcaster.sink, format="{message}", enqueue=False)

_logger = logger.opt(raw=True)
_logger_v2 = logger


def log_debug(message):
    _logger_v2.debug(message)


def log_node(message):
    _logger_v2.debug(message)


def log_error(message):
    _logger_v2.error(message)


def log_info(message):
    _logger_v2.info(message)


def log_response(message):
    _logger_v2.info(message)


def log_messages(message, *args):
    _logger.info(message)
