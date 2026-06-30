import asyncio

from langchain_core.messages import HumanMessage
from langgraph.constants import START

from src.app.llm.llm_handler.llm_handler import LLMHandler
from src.app.llm.llm_handler.chat_llm_handler import ChatLLMHandler
from src.app.llm.llm_handler.graph_llm_handler import GraphLLMHandler
from src.app.llm.services.graph_llm_service import GraphLLMService
from src.app.server.base.app_graph import AppState
from src.app.utils.logger_util import log_debug, log_response
from src.app.utils.model_util import get_default_model_config

input_text = "Write a poem about AI"

llm_config = get_default_model_config()
chat_llm_handler = ChatLLMHandler(llm_config=llm_config)


def llm_handler_demo():
    handler = LLMHandler(llm_config=llm_config)
    response = handler.execute(input_message=input_text)
    log_debug(response)
    response1 = handler.execute(input_message=[HumanMessage(input_text)])
    log_debug(response1)


async def stream_llm_handler_demo():
    handler = LLMHandler(llm_config=llm_config)
    response = handler.aexecute(input_message=input_text)
    async for chunk in await response:
        log_debug(chunk)


def chat_llm_handler_demo():
    response1 = chat_llm_handler.execute(input_message=[HumanMessage(input_text)])
    log_debug(response1)


async def stream_chat_llm_handler_demo():
    response = chat_llm_handler.aexecute(input_message=input_text)
    async for chunk in response:
        log_debug(chunk)


def response_node(app_state: AppState):
    message = app_state["messages"][-1]
    response = chat_llm_handler.execute([message])
    return {"messages": response.content}


def create_graph():
    from src.app.server.base.app_graph import AppGraph
    from langgraph.graph import StateGraph

    graph = StateGraph(AppState)
    graph.add_node("response_node", response_node)
    graph.add_edge(START, "response_node")

    app_graph = AppGraph(graph=graph)
    return app_graph


def run_graph_demo():
    graph_handler = GraphLLMHandler(graph=create_graph())
    messages = [HumanMessage(content=input_text)]
    response = graph_handler.execute(input_message={"messages": messages})
    log_response(response)


async def async_response_node(app_state: AppState, config):
    message = app_state["messages"][-1]
    response = chat_llm_handler.aexecute([message], config=config)
    log_debug("In async_response_node")
    async for chunk in response:
        yield chunk


def create_async_graph():
    from src.app.server.base.app_graph import AppGraph
    from langgraph.graph import StateGraph

    graph = StateGraph(AppState)
    graph.add_node("response_node", async_response_node)
    graph.add_edge(START, "response_node")

    app_graph = AppGraph(graph=graph)
    return app_graph


async def run_async_graph_demo():
    graph_handler = GraphLLMHandler(graph=create_async_graph())
    messages = [HumanMessage(content=input_text)]
    # async for r in await graph_handler.aexecute(input_message={"messages": messages}):
    #     log_response(r)

    graph_llm_service = GraphLLMService(llm_handler=graph_handler)
    async for r in await graph_llm_service.stream_ai(input_message={"messages": messages}):
        log_response(r)


# chat_llm_handler_demo()
# asyncio.run(stream_chat_llm_handler_demo())

# llm_handler_demo()
# asyncio.run(stream_llm_handler_demo())

# run_graph_demo()
# asyncio.run(run_async_graph_demo())
