from __future__ import annotations

from backend.app.llm.llm_handler.graph_llm_handler import GraphLLMHandler
from backend.app.llm.llm_messages.base_llm_messages import LLMInputMessageType
from backend.app.llm.services.base_llm_service import BaseLLMService


class GraphLLMService(BaseLLMService):
    def __init__(self, llm_handler: GraphLLMHandler):
        super().__init__(llm_handler=llm_handler)

    async def ask_ai(self, input_message: dict[str, LLMInputMessageType], **kwargs):
        return await self.llm_handler.execute(input_message, **kwargs)

    async def stream_ai(self, input_message: dict[str, LLMInputMessageType], **kwargs):
        return await self.llm_handler.aexecute(input_message, **kwargs)


def get_graph_llm_service(llm_handler: GraphLLMHandler) -> GraphLLMService:
    return GraphLLMService(llm_handler=llm_handler)
