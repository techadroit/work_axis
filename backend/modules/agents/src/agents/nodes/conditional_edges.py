from agents.AgentConstants import APP_MESSAGES
from agents.app_graph import AppState
from core.app_config import get_app_config

app_config = get_app_config()

def should_generate_title(state: AppState) -> str:
    messages = state.get(APP_MESSAGES, [])
    msg_count = len(messages)

    if msg_count == 1 or msg_count >= (app_config.MAX_MESSAGE_LENGTH - 1):
        return "generate_title"
    return "skip_title"