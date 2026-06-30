from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

from src.app.llm.agents.web_search.web_search_nodes import web_search_start_node, web_search_conversation_node, planning_node, \
    generator_node, retrieval_node, evaluation_agent
from src.app.server.base.app_graph import AppGraph, WebSearchState, AppState
from src.app.utils.graph_util import retry_policy


def create_web_search_agent(checkpointer=None) -> AppGraph:
    state_graph = StateGraph(WebSearchState, input_schema=AppState)
    state_graph.add_node("web_search_start_node", web_search_start_node,
                         retry_policy=retry_policy)
    state_graph.add_node("web_search_conversation_node", web_search_conversation_node)
    state_graph.add_node("planning_node", planning_node,
                         retry_policy=retry_policy)
    state_graph.add_node("retrieval_node", retrieval_node,
                         retry_policy=retry_policy)
    state_graph.add_node("generator_node", generator_node)
    state_graph.add_node("evaluation_agent", evaluation_agent)
    state_graph.add_edge(START, "web_search_start_node")
    # Conditional edge based on route_condition
    state_graph.add_conditional_edges(
        "web_search_start_node",
        route_condition
    )
    state_graph.add_edge("planning_node", "retrieval_node")
    state_graph.add_edge("retrieval_node", "generator_node")
    state_graph.add_edge("generator_node", END)
    state_graph.add_edge("retrieval_node", END)
    state_graph.add_edge("web_search_conversation_node", END)
    graph = AppGraph(graph=state_graph, emitting_node=["generator_node","web_search_conversation_node"], check_pointer=checkpointer)
    return graph

def route_condition(state):
    # Assumes state["route"] is set to either "planning_node" or "web_search_conversation_node"
    return state.get("route", "web_search_conversation_node")  # Default to web_search_conversation_node if not set



