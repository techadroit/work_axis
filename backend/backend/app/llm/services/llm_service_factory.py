from backend.app.llm.llm_handler.chat_llm_handler import ChatLLMHandler
from backend.app.llm.llm_handler.graph_llm_handler import GraphLLMHandler
from backend.app.llm.llm_handler.llm_handler import LLMHandler
from backend.app.llm.services.chat_llm_service import ChatLLMService
from backend.app.llm.services.graph_llm_service import GraphLLMService
from backend.app.llm.services.llm_service import LLMService
from backend.app.server.base.app_graph import AppGraph
from backend.app.utils.model_util import get_default_model_config


class LLMServiceFactory(object):



    @staticmethod
    def get_graph_service(graph: AppGraph) -> GraphLLMService:
        _graph_llm_handler = GraphLLMHandler(graph=graph)
        _graph_service = GraphLLMService(llm_handler=_graph_llm_handler)
        return _graph_service

    @staticmethod
    def get_new_chat_llm_service() -> ChatLLMService:
        _chat_llm_handler = ChatLLMHandler(llm_config=get_default_model_config())
        _chat_llm_service = ChatLLMService(llm_handler=_chat_llm_handler)
        return _chat_llm_service

    @staticmethod
    def get_new_llm_service() -> LLMService:
        _llm_handler = LLMHandler(llm_config=get_default_model_config())
        _llm_service = LLMService(llm_handler=_llm_handler)
        return _llm_service
