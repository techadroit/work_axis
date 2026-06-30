from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel

from src.app.server.messages.BaseChatMessage import BaseChatMessage
from src.app.server.schemas import MessageCreateRequest
from core.utils.time_util import get_utc_time

USER = "user"
ASSISTANT = "assistant"


class ChatMessageBody(BaseModel):
    messages: str


class AgentMode(str, Enum):
    DOCUMENT = "document"
    WEBSEARCH = "websearch"
    AGENT = "agent"
    OFFLINE = "offline"


class MessageType(str, Enum):
    MESSAGE = "message"
    UPDATE_TITLE = "update_title"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


# class ChatMode(BaseModel):
#     mode: AgentMode = AgentMode.OFFLINE


class ChatMessages(BaseChatMessage):
    message_id: str
    chat_session_id: str
    utc_time: str
    sender: str
    receiver: str
    message: ChatMessageBody
    chat_mode: AgentMode = AgentMode.OFFLINE
    message_type: str = MessageType.MESSAGE
    content_type: str = ContentType.TEXT
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None


def create_chat_message(messages: Union[str | ChatMessageBody], message_id: str, utc_time: str,
                        sender: str = ASSISTANT, receiver: str = USER, chat_session_id: str = "",
                        message_type=MessageType.MESSAGE,
                        content_type=ContentType.TEXT,
                        chat_mode: AgentMode = AgentMode.OFFLINE,
                        file_name: Optional[str] = None,
                        file_path: Optional[str] = None,
                        mime_type: Optional[str] = None) -> ChatMessages:
    if messages is ChatMessageBody:
        chat_message_body = messages
    else:
        chat_message_body = ChatMessageBody(messages=messages)

    return ChatMessages(
        chat_session_id=chat_session_id,
        message_id=message_id,
        utc_time=utc_time,
        sender=sender,
        receiver=receiver,
        message=chat_message_body,
        chat_mode=chat_mode,
        message_type=message_type,
        content_type=content_type,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type
    )


def convert_chat_messages_to_request(messages: ChatMessages) -> MessageCreateRequest:
    """
    Convert ChatMessages object to MessageCreateRequest schema.

    Args:
        messages: The ChatMessages object to convert

    Returns:
        MessageCreateRequest object ready for service layer
    """
    return MessageCreateRequest(
        message_id=messages.message_id,
        chat_session_id=messages.chat_session_id,
        sender=messages.sender if hasattr(messages, 'sender') else "user",
        receiver=messages.receiver if hasattr(messages, 'receiver') else None,
        messages=messages.message.messages,
        mode=messages.chat_mode if hasattr(messages, 'chat_mode') else AgentMode.OFFLINE,
        utc_time=messages.utc_time if hasattr(messages, 'utc_time') else None,
        message_type=messages.message_type,
        content_type=messages.content_type,
        file_name=messages.file_name if hasattr(messages, 'file_name') else None,
        file_path=messages.file_path if hasattr(messages, 'file_path') else None,
        mime_type=messages.mime_type if hasattr(messages, 'mime_type') else None,
    )
