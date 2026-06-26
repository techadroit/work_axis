from langchain_core.messages import SystemMessage
from langgraph.types import Overwrite

from backend.app.llm.agents.AgentConstants import APP_MESSAGES
from backend.app.llm.services.llm_service_factory import LLMServiceFactory
from backend.app.server.base.app_graph import AppState
from backend.app.server.config.app_config import get_app_config
from backend.app.utils.logger_util import log_debug

SUMMARIZATION_PROMPT = """You are a conversation summarizer. Your task is to create a concise summary of the conversation history while preserving key information.

Guidelines:
1. Capture the main topics discussed
2. Preserve important context and decisions
3. Keep user preferences and key information
4. Maintain the conversational flow
5. Be concise but comprehensive

Provide a summary that can be used as context for future conversation turns.

Conversation history to summarize:
{conversation_history}

Return ONLY the summary text without any additional formatting or explanation."""

app_config = get_app_config()

async def summarization_node(state: AppState, config) -> AppState:
    """
    Summarizes conversation history when it exceeds 20 messages.
    Keeps the system message and recent messages, replacing older messages with a summary.
    """
    log_debug(f"Entering summarization node")
    log_debug(state)
    messages = state.get(APP_MESSAGES, [])
    last_message = messages[-1]
    # Check if summarization is needed
    if len(messages) <= app_config.MAX_MESSAGE_LENGTH:
        log_debug(f"Message count ({len(messages)}) below threshold. Skipping summarization.")
        return state
    log_debug(f"Message count ({len(messages)}) exceeds threshold. Starting summarization.")
    messages_to_summarize = messages[:-1]
    conversation_messages = [msg for msg in messages_to_summarize if not isinstance(msg, SystemMessage)]
    summary_prompt = SUMMARIZATION_PROMPT.format(conversation_history=conversation_messages)
    log_debug(f"Generating conversation summary... {summary_prompt}")
    summary_response =  await LLMServiceFactory.get_new_llm_service().ask_ai(input_message=summary_prompt)
    return {APP_MESSAGES: Overwrite([summary_response, last_message])}

