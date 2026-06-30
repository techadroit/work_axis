from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.app.llm.ToolHandler import ToolHandler
from src.app.llm.configuration.embedding_configuration import EmbeddingConfiguration
from src.app.llm.configuration.llm_configuration import LlmConfiguration
from src.app.llm.llm_messages.base_llm_messages import LLMInputMessageType

""""
LLM Handler 

Role :

Create abstraction over different LLM providers
 - Provide constructors for different LLM providers

provide graph and prompt execution capabilities
    - provide a function that takes graph of type AppGraph and execute it
    - provide a function that takes prompt and execute it

provide streaming responses
    - provide a function that takes prompt and graph and provide streaming responses

provide one shot responses
    - provide a function that takes prompt and graph and provide one shot responses

will create llm instance based on configuration provided
will create embedding instance based on configuration provided
will create tool instances based on configuration provided

"""


class BaseLLMHandler(ABC):
    """Abstract base handler for all LLM interaction patterns.

    Subclasses must implement synchronous execute and asynchronous aexecute.
    Both methods accept an input_message of type LLMInputMessageType and optional **kwargs
    so that specialised handlers (graph, chat, etc.) can support additional parameters
    without modifying the base interface.
    """

    def __init__(self, llm_config: LlmConfiguration | None = None,
                 embedding_config: EmbeddingConfiguration | None = None,
                 tool_handler: ToolHandler | None = None):
        self.llm_config = llm_config
        self.embedding_config = embedding_config
        self.tool_handler = tool_handler
        # set_verbose(True)
        # set_debug(True)

    def _get_llm(self, output_model=None):
        if self.llm_config is None:
            raise ValueError("llm_config not provided")

        llm = self.llm_config.get_chat_llm()

        if output_model is not None:
            llm = llm.with_structured_output(output_model)

        if self.tool_handler is not None:
            llm = llm.bind_tools(tools=self.tool_handler.get_tools())

        return llm

    @abstractmethod
    async def execute(self, input_message: LLMInputMessageType, output_model=None,
                      **kwargs) -> Any:  # pragma: no cover - interface
        """Execute a request against the underlying LLM/provider."""
        pass

    @abstractmethod
    async def aexecute(self, input_message: LLMInputMessageType, output_model=None,
                       **kwargs) -> Any:  # pragma: no cover - interface
        """Asynchronously execute a request against the underlying LLM/provider."""
        pass

## embedding configuration
## llm configuration
## tool configuration
## chain configuration
## prompt to be executed
## response observer
