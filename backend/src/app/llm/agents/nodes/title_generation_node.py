import asyncio

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from src.app.llm.services.llm_service_factory import LLMServiceFactory
from src.app.server.base.app_graph import AppState
from src.app.utils.logger_util import log_debug


class TitleGenerationResponse(BaseModel):
    title: str = Field(
        description="A concise and descriptive title for the conversation",
        min_length=1,
        max_length=100
    )


TITLE_GENERATION_NODE = """
Generate a concise and descriptive title for the following content.
The title should capture the essence of the conversation in a few words.
You will also be provided with current title information to help you generate a better title.
Also this title can be empty if there is no title yet.

<CONVERSATION_HISTORY>
{conversation_history}
</CONVERSATION_HISTORY>
<CURRENT_TITLE>
{title}
</CURRENT_TITLE>
"""


async def generate_title_node(state: AppState):
    messages = state["messages"]
    title = state.get("chat_title", None)
    log_debug("Generating title node")
    prompt = TITLE_GENERATION_NODE.format(conversation_history=messages, title=title)
    result = await LLMServiceFactory.get_new_llm_service().ask_ai(input_message=prompt, output_model=TitleGenerationResponse)
    log_debug(result)
    return {"chat_title": result.title}


def test_generate_title_node_single_message():
    """Test title generation with single message."""
    test_state: AppState = {
        "messages": [
            HumanMessage(content="Explain quantum computing", id="msg-001")
        ],
        "chat_title": ["title", "title"]
    }

    result = asyncio.run(generate_title_node(test_state))
    log_debug(result)
    # assert "quantum computing" in result.lower()
    # assert "Explain" in result
