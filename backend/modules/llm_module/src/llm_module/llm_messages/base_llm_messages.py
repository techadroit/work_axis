from typing import Sequence, Callable, Any

from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.tools import BaseTool


class BaseLLMMessages(BaseMessage):
    pass

class AppHumanMessage(BaseLLMMessages):
    """A message type for human input in an LLM interaction."""
    pass

LLMInputMessageType = (Sequence[BaseLLMMessages] | PromptValue | str | dict[str, BaseLLMMessages])
TOOL_TYPE = Sequence[BaseTool | Callable | dict[str, Any]] | None
