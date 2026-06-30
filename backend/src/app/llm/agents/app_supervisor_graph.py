from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.app.llm.agents.AgentConstants import APP_MESSAGES
from src.app.llm.agents.agentic_mode.agent_node import agent_mode
from src.app.llm.agents.chat_mode.chat_agent_node import chat_agent_node
from src.app.llm.agents.persistence.database_check_pointer import provide_checkpointer
from src.app.llm.llm_handler.graph_llm_handler import get_graph_llm_handler
from src.app.llm.services.graph_llm_service import get_graph_llm_service
from src.app.server.messages.ChatMessages import AgentMode
from src.app.utils.logger_util import log_debug


async def app_supervisor_graph(messages, session_id, stream_handler):
    """
    Directs the incoming message to the appropriate agent/graph based on AgentMode.
    Handles streaming of responses via the provided stream_handler.
    """
    session_config: RunnableConfig = {"configurable": {"thread_id": session_id}}
    async with provide_checkpointer() as checkpointer:
        mode = messages.chat_mode
        if mode == AgentMode.AGENT:
            log_debug("Supervisor: Routing to agent (conversation) graph.")
            human_message = HumanMessage(messages.message.messages)
            graph = agent_mode(checkpointer)
            graph_handler = get_graph_llm_handler(graph=graph)
            graph_service = get_graph_llm_service(graph_handler)
            async for stream in await graph_service.stream_ai({APP_MESSAGES: [human_message]},
                                                              session_config=session_config):
                await stream_handler.handle_stream(stream, chat_session_id=session_id,
                                                   emitting_node=graph.get_emitting_node())
        else:  # AgentMode.NONE or any other fallback
            log_debug("Supervisor: Routing to default conversation graph.")
            human_message = HumanMessage(messages.message.messages)
            graph = chat_agent_node(checkpointer)
            graph_handler = get_graph_llm_handler(graph=graph)
            graph_service = get_graph_llm_service(graph_handler)
            async for stream in await graph_service.stream_ai({APP_MESSAGES: [human_message]},
                                                              session_config=session_config):
                await stream_handler.handle_stream(stream, chat_session_id=session_id,
                                                   emitting_node=graph.get_emitting_node())
