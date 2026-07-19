from langchain_core.messages import SystemMessage, ToolMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END

from llm_module.ToolHandler import ToolHandler
from agents.AgentConstants import APP_MESSAGES
from agents.email_search.email_agent_tools import search_emails_tool
from llm_module.llm_handler.chat_llm_handler import ChatLLMHandler
from llm_module.services.chat_llm_service import get_chat_llm_service
from agents.services.llm_service_factory import LLMServiceFactory
from src.app.prompts.markdown_response_format import mark_down_response_format
from agents.app_graph import AppGraph, EmailState
from core.utils.logger_util import log_debug
from src.app.utils.model_util import get_default_model_config

tools = [search_emails_tool]

ANSWER_SYSTEM_PROMPT = f"""
<ROLE>
You are a helpful and concise email assistant.
You will receive a response from an email agent who retrieved information from the user's emails.
Your task is to provide a final answer to the user's query based on the information provided by the agent.
Cite the sender and subject of relevant emails where helpful.
If the information is insufficient, respond with "I don't know."
</ROLE>
<ConversationHistory>
{{conversation_history}}
</ConversationHistory>
{mark_down_response_format}
"""

EMAIL_ANALYSIS_SYSTEM_PROMPT = """
## You are an email analyzer designed to search the user's ingested emails to provide accurate and relevant information.
## You will be provided with a search tool and have to use it (possibly multiple times) to gather information.
## Your goal is to generate search queries to find relevant emails using the tool provided to you.
## After every time you receive information you have to analyze it and reflect if you have sufficient information to answer the user's query.
## If you don't have sufficient information you have to generate a new search query to find more relevant information.
## You can call the tool up to 3 times to gather information.
## Once you feel you have enough findings to answer the user's query you have to provide a concise summary of your findings.

<ConversationHistory>
"""


def create_email_agent_graph(checkpointer=None):
    """
    Create an agentic RAG graph for email search using the ReAct pattern.

    Graph flow:
    START -> agent -> (continue -> agent [loop] OR answer -> answer) -> END

    The agent can call search_emails up to 3 times to gather information,
    then routes to the answer node for final response generation.
    """
    graph = StateGraph(EmailState)
    graph.add_node("agent", email_agent_node)
    graph.add_node("answer", answer_node)
    graph.add_node("tool_node", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", email_router,
                                {"tool_call": "tool_node", "agent_call": "agent", "answer_call": "answer"})
    graph.add_edge("tool_node", "agent")
    graph.add_edge("answer", END)

    return AppGraph(graph=graph, check_pointer=checkpointer, emitting_node=["answer"])


def _build_context_messages(messages: list) -> list:
    """The checkpointer persists the WHOLE session's message history (by
    design, for conversational continuity). Feeding all of it - including
    raw intermediate tool-calls/tool-results from completed prior turns -
    into the LLM on every new question makes a small model conflate old,
    unrelated answers with the current one (e.g. an earlier "AWS email"
    answer bleeding into a later, unrelated question).

    Trimming down to ONLY the current turn (dropping all prior turns
    entirely) fixes the bleed-through but also throws away legitimate
    follow-up context ("what about the other one?").

    Middle ground: for every COMPLETED prior turn, keep just the
    HumanMessage (the question) and that turn's final AIMessage (the
    condensed answer) - dropping the noisy intermediate tool-call
    AIMessages and raw ToolMessage content that caused the bleed-through.
    The CURRENT (most recent) turn keeps everything, so its own in-progress
    ReAct loop still sees its own tool calls/results correctly.
    """
    human_indices = [i for i, m in enumerate(messages) if isinstance(m, HumanMessage)]
    if not human_indices:
        return messages

    current_turn_start = human_indices[-1]
    result = []
    for position, human_idx in enumerate(human_indices):
        turn_end = human_indices[position + 1] if position + 1 < len(human_indices) else len(messages)
        turn_messages = messages[human_idx:turn_end]

        if human_idx == current_turn_start:
            result.extend(turn_messages)
            continue

        # Completed turn: keep the question + the final (non-tool-call) answer only.
        result.append(turn_messages[0])
        final_ai = next(
            (m for m in reversed(turn_messages) if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None)),
            None,
        )
        if final_ai is not None:
            result.append(final_ai)

    return result


async def tool_node(state):
    log_debug(f"Email tool node entered with state: {state}")
    result = []
    for tool_call in state[APP_MESSAGES][-1].tool_calls:
        if tool_call["name"] == "search_emails":
            args = tool_call["args"]
            tool_result = search_emails_tool.invoke(
                {"user_id": state.get("user_id"),
                 "query": args.get("query"),
                 "top_k": args.get("top_k", 10)
                 })
        else:
            # A hallucinated tool name must still get a ToolMessage reply -
            # leaving a tool call dangling breaks the chat protocol (provider
            # errors) and would loop the router forever on the same message.
            tool_result = f"Unknown tool '{tool_call['name']}' - only 'search_emails' is available."
        result.append(
            ToolMessage(
                tool_call_id=tool_call["id"],
                content=tool_result,
                name=tool_call["name"]
            )
        )
    return {APP_MESSAGES: result}


async def email_agent_node(state: EmailState, config: RunnableConfig):
    """
    Agent node that implements ReAct pattern:
    1. Calls LLM with tool access
    2. If tools are called, executes them and adds results to messages
    3. Tracks tool call count (max 3)
    """
    log_debug(f"Email Agent node entered with state {state}")
    messages = _build_context_messages(state["messages"])
    llm_config = get_default_model_config()
    llm_handler = ChatLLMHandler(llm_config=llm_config, tool_handler=ToolHandler.create(tools=tools))
    chat_llm_service = get_chat_llm_service(llm_handler=llm_handler)
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=EMAIL_ANALYSIS_SYSTEM_PROMPT)] + messages
    response = await chat_llm_service.ask_ai(input_message=messages)
    return {"messages": response, "session_id": state.get("session_id", None), "user_id": state.get("user_id", None)}


async def answer_node(state: EmailState, config, writer):
    log_debug(f"Email answer node entered with state \n {state}")
    messages = _build_context_messages(state[APP_MESSAGES])
    system_prompt = ANSWER_SYSTEM_PROMPT.format(
        conversation_history=messages
    )
    llm_service = LLMServiceFactory.get_new_llm_service()
    full_response = ""
    async for stream in llm_service.stream_ai(input_message=system_prompt, config=config):
        full_response += stream.content
        writer({APP_MESSAGES: stream.content})
    return {APP_MESSAGES: AIMessage(full_response)}


_MAX_TOOL_ROUNDS_PER_TURN = 3


def email_router(state: EmailState) -> str:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call.

    Enforces the "up to 3 tool calls" limit the system prompt promises: the
    prompt alone doesn't bind the model, and without a hard cap a model that
    keeps emitting tool calls would loop agent -> tool -> agent indefinitely.
    Counted per current turn (ToolMessages after the last HumanMessage).
    """
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "answer_call"

    rounds_this_turn = 0
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            break
        if isinstance(m, ToolMessage):
            rounds_this_turn += 1
    if rounds_this_turn >= _MAX_TOOL_ROUNDS_PER_TURN:
        log_debug(f"Email agent hit tool-call cap ({_MAX_TOOL_ROUNDS_PER_TURN}) - forcing answer")
        return "answer_call"
    return "tool_call"
