import operator
from typing import Annotated, Any, Dict, List, Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, add_messages
from typing_extensions import TypedDict


class AppGraph:

    def __init__(self, graph: StateGraph,
                 check_pointer=None,
                 emitting_node: [str] = None):
        self.graph = graph
        self.emitting_node = emitting_node
        self.check_pointer = check_pointer

    def set_checkpointer(self, checkpointer):
        self.check_pointer = checkpointer

    def get_graph(self, **kwargs):
        return self.graph.compile(checkpointer=self.check_pointer)

    def get_emitting_node(self) -> [str]:
        return self.emitting_node

def overwrite_reducer(existing, new):
    """Always overwrites with new value, even if None."""
    return new


class AppState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list[AnyMessage], add_messages]
    route: Optional[str] = None
    chat_title: Annotated[Optional[str], overwrite_reducer]
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ConversationState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: Optional[str] = None


class WebSearchState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list[AnyMessage], add_messages]
    knowledge_base: Optional[List[Dict[str, Any]]] = None  # List of dicts for extracted web content
    search_query: Optional[List[str]] = None
    route: Optional[str] = None
    session_id: Optional[str] = None

class DocumentState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list[AnyMessage], add_messages]
    document_chunks: Optional[List[Dict[str, Any]]] = None  # List of dicts for document chunks
    document_metadata: Optional[Dict[str, Any]] = None  # Metadata about the document
    tool_calls: Optional[List[Dict[str, Any]]] = None  # Tool calls from the agent
    final_answer: Optional[str] = None  # Final answer from the agent
    session_id: Optional[str] = None


class EmailState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: Optional[str] = None
    user_id: Optional[str] = None
