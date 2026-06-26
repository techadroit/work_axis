from backend.app.llm.llm_handler.base_llm_handler import BaseLLMHandler
from backend.app.llm.llm_handler.llm_handler import LLMHandler
from backend.app.llm.llm_messages.base_llm_messages import LLMInputMessageType
from backend.app.llm.services.base_llm_service import BaseLLMService


class LLMService(BaseLLMService):

    def __init__(self, llm_handler: LLMHandler = None):
        self.llm_handler = llm_handler

    async def ask_ai(self, input_message: LLMInputMessageType, output_model=None, **kwargs):
        return self.llm_handler.execute(input_message, output_model=output_model, **kwargs)

    async def stream_ai(self, input_message: LLMInputMessageType, config=None, output_model=None, **kwargs):
        async for stream in self.llm_handler.aexecute(input_message, config=config, output_model=output_model,
                                                      **kwargs):
            yield stream


def get_llm_service(llm_handler: BaseLLMHandler = None) -> LLMService:
    return LLMService(llm_handler=llm_handler)
