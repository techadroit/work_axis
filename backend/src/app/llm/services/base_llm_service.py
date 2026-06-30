from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.app.llm.llm_handler.base_llm_handler import BaseLLMHandler
from src.app.llm.llm_messages.base_llm_messages import LLMInputMessageType


class BaseLLMService(ABC):
    """Abstract service layer for LLM handlers.

    Provides a uniform async interface for asking the model (single response)
    and streaming responses. Concrete subclasses specialise input message
    structure (chat vs graph).
    """

    def __init__(self, llm_handler: BaseLLMHandler):
        self.llm_handler = llm_handler

    @abstractmethod
    async def ask_ai(self, input_message: Any, **kwargs):
        """Execute a single request against the handler."""
        pass

    @abstractmethod
    async def stream_ai(self, input_message: Any, config=None, **kwargs):
        """Stream responses from the handler (returns/iterates async generator)."""
        pass

