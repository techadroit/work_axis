from typing import Any

from llm_module.ToolHandler import ToolHandler
from llm_module.configuration.embedding_configuration import EmbeddingConfiguration
from llm_module.configuration.llm_configuration import LlmConfiguration
from llm_module.llm_handler.base_llm_handler import BaseLLMHandler
from llm_module.llm_messages.base_llm_messages import LLMInputMessageType
from agents.app_graph import AppGraph


class GraphLLMHandler(BaseLLMHandler):

    def __init__(self, llm_config: LlmConfiguration = None,
                 embedding_config: EmbeddingConfiguration = None,
                 tool_handler: ToolHandler = None,
                 graph: AppGraph = None):
        super().__init__(llm_config=llm_config,
                         embedding_config=embedding_config,
                         tool_handler=tool_handler)
        self.agent = graph.get_graph() if graph else None

    async def execute(self, input_message: LLMInputMessageType, output_model=None, **kwargs) -> Any:
        if self.agent is None:
            raise ValueError("Graph agent not provided")

        session_config = kwargs.pop("session_config", None)
        return await self.agent.ainvoke(input_message, config=session_config)

    async def aexecute(self, input_message: LLMInputMessageType, output_model=None, **kwargs) -> Any:
        if self.agent is None:
            raise ValueError("Graph agent not provided")
        session_config = kwargs.pop("session_config", None)
        stream_events = kwargs.pop("stream_events", ["messages", "updates"])
        return self.agent.astream(input_message, stream_mode=stream_events, subgraphs=True,
                                  config=session_config)


def get_graph_llm_handler(llm_config=None, embedding_config=None, tool_handler=None, graph=None) -> GraphLLMHandler:
    return GraphLLMHandler(llm_config=llm_config,
                           embedding_config=embedding_config,
                           tool_handler=tool_handler,
                           graph=graph)
