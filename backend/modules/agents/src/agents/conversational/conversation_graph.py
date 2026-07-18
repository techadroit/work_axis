from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.constants import START
from langgraph.graph import StateGraph

from agents.AgentConstants import APP_MESSAGES
from llm_module.llm_handler.chat_llm_handler import ChatLLMHandler, get_chat_llm_handler
from agents.llm_handler.graph_llm_handler import GraphLLMHandler
from llm_module.services.chat_llm_service import get_chat_llm_service
from agents.services.graph_llm_service import get_graph_llm_service
from agents.app_graph import AppGraph, ConversationState
from core.utils.logger_util import log_debug, log_response
from src.app.utils.model_util import get_default_model_config

_conversation_system_prompt = """
    You are a friendly and helpful assistant.
    Your task is to respond conversationally to the user's message. 
    If the user asks about something discussed earlier, look up the chat history to provide a relevant answer. 
    If the answer can be found in the chat history, use that information.
     If not, reply naturally as a helpful assistant would.
    Do not use any external or internet information. 
    Only use the chat history and your general conversational abilities.
    Always keep your responses clear, concise, and polite.
    
    Your response should be in markdown format when appropriate, using headings, bullet points, or code blocks as needed.
    """

# llm_service = get_chat_llm_service(llm_handler=ChatLLMHandler(llm_config=get_default_model_config()))


def create_conversation_graph(checkpointer=None) -> AppGraph:
    graph = StateGraph(ConversationState)
    graph.add_node(conversation_node)
    graph.add_edge(START, "conversation_node")
    return AppGraph(graph, check_pointer=checkpointer)


async def conversation_node(state: ConversationState, config, writer):
    """
    A placeholder function for the conversation node.
    This function can be expanded to include specific logic for conversations.
    """
    log_debug("entering conversation node")
    log_debug(state)
    input_messages = [SystemMessage(_conversation_system_prompt)] + state.get(APP_MESSAGES, [])
    llm_handler = get_chat_llm_handler(llm_config=get_default_model_config())
    llm_service = get_chat_llm_service(llm_handler=llm_handler)
    full_response = ""
    async for stream in llm_service.stream_ai(input_message=input_messages, config=config):
        full_response += stream.content
        writer({APP_MESSAGES: stream.content})
    return {APP_MESSAGES: AIMessage(full_response)}


async def run_demo():
    graph = create_conversation_graph()
    messages = HumanMessage("Hello")
    async with AsyncSqliteSaver.from_conn_string(":memory:") as checkpointer:
        graph.set_checkpointer(checkpointer)
        graph_handler = GraphLLMHandler(graph=graph)
        graph_service = get_graph_llm_service(llm_handler=graph_handler)
        async for stream in await graph_service.stream_ai(input_message={"messages": [messages]},
                                                          session_config={
                                                              "configurable": {"thread_id": "demo_thread"}}):
            log_response("Streamed graph Response:")
            log_debug(stream)

# asyncio.run(run_demo())
