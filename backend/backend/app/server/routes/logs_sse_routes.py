"""
Server-Sent Events (SSE) endpoint for streaming live application logs.

Connect with:
    GET /api/logs/stream

The stream emits newline-delimited SSE frames:
    data: {"time": "...", "level": "INFO", "message": "...", "name": "...", "function": "...", "line": N}

A ": keep-alive" comment is sent every 15 seconds when no logs arrive so
that proxies and browsers do not close idle connections.
"""

import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.app.utils.logger_util import log_broadcaster

logs_sse_router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)


@logs_sse_router.get(
    "/stream",
    summary="Stream live application logs via SSE",
    response_class=StreamingResponse,
)
async def stream_logs():
    """
    Open a Server-Sent Events connection to receive all application log records
    in real time.  Each event is a JSON object with the fields:
    - **time** – timestamp (YYYY-MM-DD HH:MM:SS.mmm)
    - **level** – log level (DEBUG / INFO / WARNING / ERROR / CRITICAL)
    - **message** – the log message
    - **name** – logger / module name
    - **function** – calling function name
    - **line** – source line number
    """
    queue = log_broadcaster.subscribe()

    async def event_generator():
        try:
            while True:
                try:
                    log_entry = await asyncio.wait_for(queue.get(), timeout=15.0)
                    data = json.dumps(log_entry)
                    # SSE format: each field on its own line, blank line terminates the event
                    yield f"event: log\ndata: {data}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive comment so the connection isn't dropped
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            log_broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",   # disable Nginx buffering
        },
    )

