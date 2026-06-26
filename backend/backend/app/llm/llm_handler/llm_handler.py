# from langchain.globals import set_debug, set_verbose
from typing import Any

from backend.app.llm.llm_handler.base_llm_handler import BaseLLMHandler
from backend.app.llm.llm_messages.base_llm_messages import LLMInputMessageType


# set_debug(True)
# set_verbose(True)

class LLMHandler(BaseLLMHandler):

    def execute(self, input_message: LLMInputMessageType, output_model=None, **kwargs) -> Any:
        return self._get_llm(output_model).invoke(input_message)

    async def aexecute(self, input_message: LLMInputMessageType, output_model=None, **kwargs) -> Any:
        config = kwargs.pop("config", None)
        async for chunk in self._get_llm(output_model).astream(input_message, config):
            yield chunk


def get_llm_handler(llm_config=None, embedding_config=None, tool_handler=None) -> LLMHandler:
    return LLMHandler(llm_config=llm_config,
                      embedding_config=embedding_config,
                      tool_handler=tool_handler)
