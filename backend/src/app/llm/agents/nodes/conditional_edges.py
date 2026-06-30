from src.app.llm.agents.AgentConstants import APP_MESSAGES
from src.app.server.base.app_graph import AppState
from src.app.server.config.app_config import get_app_config

app_config = get_app_config()

def should_generate_title(state: AppState) -> str:
    messages = state.get(APP_MESSAGES, [])
    msg_count = len(messages)

    if msg_count == 1 or msg_count >= (app_config.MAX_MESSAGE_LENGTH - 1):
        return "generate_title"
    return "skip_title"