from typing import Any, Optional

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from backend.app.llm.agents.conversational.conversation_graph import create_conversation_graph
from backend.app.llm.agents.persistence.database_check_pointer import provide_checkpointer
from backend.app.utils.logger_util import log_info, log_error


def extract_ai_message(chunk: Any) -> Optional[AIMessage]:
    """
    Return the AIMessage if the streamed chunk matches the expected
    structure: ("messages", (AIMessage, metadata_dict)).
    """
    if (
            isinstance(chunk, tuple) and len(chunk) == 2 and chunk[0] == "messages"
            and isinstance(chunk[1], tuple) and len(chunk[1]) >= 1
            and isinstance(chunk[1][0], AIMessage)
    ):
        return chunk[1][0]
    return None


# Example usage inside your loop:
# msg = extract_ai_message(chunk)
# if msg:
#     full_response += msg.content

def get_session_config(session_Id: str) -> RunnableConfig:
    """Generate a unique session ID."""
    session_config: RunnableConfig = {"configurable": {"thread_id": session_Id}}
    return session_config


async def add_messages_to_graph(session_id, message, **kwargs):
    try:
        session_config = get_session_config(session_id)
        log_info(f"session config:{session_config}")
        async with provide_checkpointer() as checkpointer:
            graph = create_conversation_graph(checkpointer=checkpointer).get_graph()
            await graph.aupdate_state(config=session_config, values={"messages": message})
            log_info("State updated with document message.")
    except Exception as e:
        log_error(f"Failed to create file message: {str(e)}")
        raise Exception(f"Failed to add document message: {str(e)}")


async def delete_graph(session_id, **kwargs):
    try:
        session_config = get_session_config(session_id)
        log_info(f"session config:{session_config}")
        async with provide_checkpointer() as checkpointer:
            checkpointer.adelete_thread(thread_id=session_id)
            log_info("State updated with document message.")
    except Exception as e:
        log_error(f"Failed to create file message: {str(e)}")
        raise Exception(f"Failed to add document message: {str(e)}")


async def is_last_chunk(message: Any) -> bool:
    """
    Check if the given chunk is the last chunk in a stream.
    """
    if message.chunk_position is not None and message.chunk_position == "last":
        return True
    return False
