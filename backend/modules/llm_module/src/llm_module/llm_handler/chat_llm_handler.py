from typing import Any

from llm_module.ToolHandler import ToolHandler
from llm_module.configuration.embedding_configuration import EmbeddingConfiguration
from llm_module.configuration.llm_configuration import LlmConfiguration
from llm_module.llm_handler.base_llm_handler import BaseLLMHandler
from llm_module.llm_messages.base_llm_messages import LLMInputMessageType


class ChatLLMHandler(BaseLLMHandler):

    def __init__(self, llm_config: LlmConfiguration = None,
                 embedding_config: EmbeddingConfiguration = None,
                 tool_handler: ToolHandler = None):
        super().__init__(llm_config=llm_config,
                         embedding_config=embedding_config,
                         tool_handler=tool_handler)

    def execute(self, input_message: LLMInputMessageType,output_model=None, **kwargs) -> Any:
        return self._get_llm(output_model).invoke(input_message)

    async def aexecute(self, input_message: LLMInputMessageType,output_model=None, **kwargs):
        config = kwargs.pop("config", None)
        async for chunk in self._get_llm(output_model).astream(input_message, config):
            yield chunk


def get_chat_llm_handler(llm_config=None, embedding_config=None, tool_handler=None) -> ChatLLMHandler:
    return ChatLLMHandler(llm_config=llm_config,
                          embedding_config=embedding_config,
                          tool_handler=tool_handler)
