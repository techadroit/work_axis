from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from core.errors import RetryableError
from src.app.llm.agents.AgentConstants import APP_MESSAGES
from src.app.llm.agents.conversational.conversation_graph import create_conversation_graph
from src.app.llm.agents.doc_search.document_agent_graph import create_document_agent_graph
from src.app.llm.agents.nodes.conditional_edges import should_generate_title
from src.app.llm.agents.nodes.summarization_node import summarization_node
from src.app.llm.agents.nodes.title_generation_node import generate_title_node
from src.app.llm.agents.web_search.web_search_agents import create_web_search_agent
from src.app.llm.services.llm_service_factory import LLMServiceFactory
from src.app.server.base.app_graph import AppState, AppGraph
from core.app_config import get_app_config
from src.app.utils.graph_util import retry_policy
from src.app.utils.logger_util import log_debug
from src.app.utils.prompt_util import format_prompt

app_config = get_app_config()


class AgentRouteResponse(BaseModel):
    route: Literal["conversation", "web_search", "document_search"] = Field(
        description="The selected route based on user intent"
    )


AGENT_ROUTER_PROMPT = """
You are an expert query router for a chat llm application. 
Your only goal is to analyze the conversation and decide which route to take based on the following available routes.
You will be provided with chat history between a user and an AI assistant.

## Your task:
- Analyze Conversation History and decide which route to select.
- You will be provided with multiple questions from the user but you should select only one route.
- Based on the user intent, choose one of the available routes.
- Never select multiple routes.
- If you are uncertain about which route to choose, default to "conversation".

### Available Routes:
1. **conversation** - For greetings, farewells, or questions answerable from conversation history
2. **web_search** - For queries requiring current/external information from the internet
3. **document_search** - For queries about uploaded documents or files

### Important Rules:
- Multiple routes are not allowed.
- Output only one route based on the user intent based on the conversation history
- Output ONLY valid JSON in the exact format shown
- Do not include reasoning, explanations, or multiple responses
- If uncertain, default to "conversation"

<ConversationHistory>
{conversation_history}
</ConversationHistory>
"""


def agent_mode(checkpointer=None, session_id=None) -> AppGraph:
    document_node = create_document_agent_graph(checkpointer=None)
    web_search_node = create_web_search_agent(checkpointer=None)
    conversation_node = create_conversation_graph(checkpointer=None)
    graph = StateGraph(AppState)
    graph.add_node("summarization_node", summarization_node)
    graph.add_node("title_generation_node", generate_title_node)
    graph.add_node("agent_router_node", agent_router_node,
                   retry_policy=retry_policy)
    graph.add_node("conversation_node", conversation_node.get_graph())
    graph.add_node("document_node", document_node.get_graph())
    graph.add_node("web_search_node", web_search_node.get_graph())
    graph.add_conditional_edges(
        "summarization_node",
        should_generate_title,
        {
            "generate_title": "title_generation_node",
            "skip_title": END
        }
    )
    graph.add_conditional_edges(
        "agent_router_node",
        agent_route_condition,
        {
            "web_search": "web_search_node",
            "document_search": "document_node",
            "conversation": "conversation_node"
        })

    graph.add_edge(START, "summarization_node")
    graph.add_edge("summarization_node", "agent_router_node")
    graph.add_edge("title_generation_node", END)
    graph.add_edge("web_search_node", END)
    graph.add_edge("conversation_node", END)
    graph.add_edge("document_node", END)
    graph = AppGraph(graph=graph,
                     emitting_node=["generator_node", "web_search_conversation_node", "answer", "conversation_node"],
                     check_pointer=checkpointer)
    return graph


def agent_route_condition(state) -> str:
    return state.get("route", "")


async def agent_router_node(state: AppState, config: RunnableConfig = None) -> AppState:
    if config is not None:
        state["session_id"] = config.get("configurable", {}).get("thread_id", None)
    log_debug(f"Agent router node: {state}")
    messages = state[APP_MESSAGES]
    prompt = format_prompt(AGENT_ROUTER_PROMPT, conversation_history=messages)
    llm_service = LLMServiceFactory.get_new_llm_service()
    try:
        response = await llm_service.ask_ai(prompt, output_model=AgentRouteResponse)
        route = response.route
    except Exception as e:
        log_debug(f"Error parsing agent router response: {e} | Response content: {response.content}")
        raise RetryableError("Failed to parse agent router response")
    log_debug(f" the route is {route}")
    state["route"] = route
    return state
