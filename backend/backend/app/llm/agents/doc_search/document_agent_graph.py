from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

from backend.app.llm.ToolHandler import ToolHandler
from backend.app.llm.agents.AgentConstants import APP_MESSAGES
from backend.app.llm.agents.doc_search.document_agent_tools import search_documents_tool
from backend.app.llm.llm_handler.chat_llm_handler import ChatLLMHandler
from backend.app.llm.services.chat_llm_service import get_chat_llm_service
from backend.app.llm.services.llm_service_factory import LLMServiceFactory
from backend.app.prompts.markdown_response_format import mark_down_response_format
from backend.app.server.base.app_graph import AppGraph, DocumentState
from backend.app.utils.logger_util import log_debug
from backend.app.utils.model_util import get_default_model_config

# Get LLM
tools = [search_documents_tool]

ANSWER_SYSTEM_PROMPT = f"""
<ROLE>
You are a helpful and concise document analysis assistant. 
You will receive response from an document agent who will retrieve information from a set of documents. 
Your task is to provide a final answer to the user's query based on the information provided by the agent.
Provide clear and accurate answers based on the information retrieved from the documents. 
If the information is insufficient, respond with "I don't know."
</ROLE>
<ConversationHistory>
{{conversation_history}}
</ConversationHistory>
{mark_down_response_format}
"""

DOCUMENT_ANALYSIS_SYSTEM_PROMPT = """


## You are a document analyzer designed to search and analyze documents to provide accurate and relevant information.
## you will be provided with list of tools and you have to use that tools multiple times to gather information and document your findings.
## Your goal is to generate query to find similar document from the vector store using tools provided to you. 
## After every time you receive information you have to analyze it and reflect if you have sufficient information to answer the user's query.
## If you don't have sufficient information you have to generate new search query to find more relevant information.
## You can call the tools up to 3 times to gather information.
## Once you feel you have enough findings to answer the user's query you have to provide a concise summary of your findings.


## Use the attached tool to search documents as needed to find relevant information.
 the tools multiple times if necessary to gather sufficient information.
## Generate new search queries based on previous results to refine your search.
## When you have enough information to answer the user's query create a concise finding that could be used by other agents to generate answers.

## After you receive documents or information from the tool search grade it reflect it and check if this information is sufficient to answer the user's query.
## If you need more information, generate a new search query and call the tool again.
## If you have sufficient information to answer the user's query, provide a concise summary of your findings


<ConversationHistory>
"""


def create_document_agent_graph(checkpointer=None):
    """
    Create an agentic RAG graph for document analysis using ReAct pattern.

    Graph flow:
    START -> agent_node -> (continue -> agent_node [loop] OR answer -> answer_node) -> END

    The agent can call search tools multiple times (up to 3) to gather information,
    then routes to the answer node for final response generation.
    """
    graph = StateGraph(DocumentState)
    graph.add_node("agent", document_agent_node)
    graph.add_node("answer", answer_node)
    graph.add_node("tool_node", tool_node)

    # Set up edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", doc_router,
                                {"tool_call": "tool_node", "agent_call": "agent", "answer_call": "answer"})
    graph.add_edge("tool_node", "agent")
    graph.add_edge("answer", END)

    return AppGraph(graph=graph, check_pointer=checkpointer, emitting_node=["answer"])


async def tool_node(state):
    log_debug(f"Tool Node entered with state: {state}")
    result = []
    for tool_call in state[APP_MESSAGES][-1].tool_calls:
        if tool_call["name"] == "search_documents":
            args = tool_call["args"]
            tool_result = search_documents_tool.invoke(
                {"session_id": state["session_id"],
                 "query": args.get("query"),
                 "top_k": args.get("top_k", 5)
                 })
            result.append(
                ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=tool_result,
                    name=tool_call["name"]
                )
            )
    result = {APP_MESSAGES: result}
    log_debug("tool call")
    log_debug(result)
    return result


async def document_agent_node(state: DocumentState, config: RunnableConfig):
    """
    Agent node that implements ReAct pattern:
    1. Calls LLM with tool access
    2. If tools are called, executes them and adds results to messages
    3. Tracks tool call count (max 3)
    """

    log_debug(f"Document Agent node entered with state {state}")
    messages = state["messages"]
    llm_config = get_default_model_config()
    llm_handler = ChatLLMHandler(llm_config=llm_config, tool_handler=ToolHandler.create(tools=tools))
    chat_llm_service = get_chat_llm_service(llm_handler=llm_handler)
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=DOCUMENT_ANALYSIS_SYSTEM_PROMPT)] + messages
        log_debug("adding system prompt to messages")
        log_debug(messages)
    response = await chat_llm_service.ask_ai(input_message=messages)
    log_debug("Document Agent LLM response:")
    log_debug(response)
    return {"messages": response, "session_id": state.get("session_id", None)}


async def answer_node(state: DocumentState, config, writer):
    log_debug(f"Answer node entered with state \n {state}")
    messages = state[APP_MESSAGES]
    system_prompt = ANSWER_SYSTEM_PROMPT.format(
        conversation_history=messages
    )
    llm_service = LLMServiceFactory.get_new_llm_service()
    full_response = ""
    async for stream in llm_service.stream_ai(input_message=system_prompt, config=config):
        full_response += stream.content
        writer({APP_MESSAGES: stream.content})
    return {APP_MESSAGES: AIMessage(full_response)}


def doc_router(state: DocumentState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # log_debug(f"last_message in doc_router: {last_message.tool_calls}")
    result = None
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        result = "tool_call"
    else:
        result = "answer_call"
    # log_debug(f"Document router returned {result}")
    return result
