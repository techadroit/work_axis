from src.app.server.messages.ChatMessages import ChatMessages
import json

from src.app.utils.logger_util import log_messages


def parse_message(message: str) -> ChatMessages:
    """
    Parses a JSON message string into a ChatMessages object.

    Args:
        message (str): The raw JSON message string.

    Returns:
        ChatMessages: A parsed ChatMessages object.

    Raises:
        ValueError: If the message format is invalid.
    """
    try:
        log_messages(f"Raw incoming message: {repr(message)}")
        # Parse JSON string to dictionary
        message_dict = json.loads(message)

        # Create ChatMessages from dictionary using Pydantic
        return ChatMessages(**message_dict)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Invalid message format: {str(e)}")

