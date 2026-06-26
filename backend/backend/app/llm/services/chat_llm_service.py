from __future__ import annotations

from backend.app.llm.llm_handler.chat_llm_handler import ChatLLMHandler
from backend.app.llm.llm_messages.base_llm_messages import LLMInputMessageType
from backend.app.llm.services.base_llm_service import BaseLLMService


class ChatLLMService(BaseLLMService):
    def __init__(self, llm_handler: ChatLLMHandler):
        super().__init__(llm_handler=llm_handler)

    async def ask_ai(self, input_message: LLMInputMessageType, **kwargs):
        return self.llm_handler.execute(input_message, **kwargs)

    async def stream_ai(self, input_message: LLMInputMessageType, config=None, **kwargs):
        async for streams in self.llm_handler.aexecute(input_message, config=config, **kwargs):
            yield streams


def get_chat_llm_service(llm_handler: ChatLLMHandler) -> ChatLLMService:
    return ChatLLMService(llm_handler=llm_handler)
