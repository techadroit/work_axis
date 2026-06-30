from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.app.llm.agents.conversational.conversation_graph import create_conversation_graph
from src.app.llm.agents.nodes.conditional_edges import should_generate_title
from src.app.llm.agents.nodes.summarization_node import summarization_node
from src.app.llm.agents.nodes.title_generation_node import generate_title_node
from src.app.server.base.app_graph import AppState, AppGraph


def chat_agent_node(checkpointer=None):
    conversation_node = create_conversation_graph(checkpointer=None)
    graph = StateGraph(AppState)
    graph.add_node("summarization_node", summarization_node)
    graph.add_node("title_generation_node", generate_title_node)
    graph.add_node("conversation_node", conversation_node.get_graph())

    graph.add_conditional_edges(
        "summarization_node",
        should_generate_title,
        {
            "generate_title": "title_generation_node",
            "skip_title": END
        }
    )

    graph.add_edge(START, "summarization_node")
    graph.add_edge("summarization_node", "conversation_node")
    graph.add_edge("title_generation_node", END)

    graph.add_edge("conversation_node", END)

    return AppGraph(graph=graph, emitting_node=["conversation_node"], check_pointer=checkpointer)
