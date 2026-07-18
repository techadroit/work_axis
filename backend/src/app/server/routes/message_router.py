from agents.app_supervisor_graph import app_supervisor_graph
from src.app.server.base.base_stream_handler import BaseStreamHandler
from src.app.server.messages.ChatMessages import ChatMessages, convert_chat_messages_to_request
from src.app.server.service import ChatMessageService
from src.app.utils.logger_util import log_debug


class MessageService:
    def __init__(self):
        self.chat_message_service = ChatMessageService()

    async def save_messages(self, messages: ChatMessages):
        self.chat_message_service.save_message(request = convert_chat_messages_to_request(messages))

    async def handle_messages(self, messages: ChatMessages, session_id: str, stream_handler: BaseStreamHandler = None):
        log_debug(messages)
        await self.save_messages(messages)
        await app_supervisor_graph(messages, messages.chat_session_id, stream_handler)
