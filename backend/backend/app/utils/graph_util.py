from typing import Literal

from langgraph._internal._retry import default_retry_on
from langgraph.graph import END, MessagesState
from langgraph.types import RetryPolicy

from backend.app.base.custom_errors import RetryableError


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return "answer"


def app_error_retry_on(exc: Exception) -> bool:
    """Custom retry logic for the app supervisor graph."""
    # Here you can implement custom logic to determine if the exception is transient
    # For simplicity, we will retry on all exceptions except ValueError
    if isinstance(exc, RetryableError):
        return True
    return default_retry_on(exc)


retry_policy = RetryPolicy(max_attempts=3, initial_interval=1.0, retry_on=app_error_retry_on)
