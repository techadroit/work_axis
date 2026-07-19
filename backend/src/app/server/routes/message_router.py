import asyncio
from collections import defaultdict

from agents.app_supervisor_graph import app_supervisor_graph
from src.app.server.base.base_stream_handler import BaseStreamHandler
from src.app.server.messages.ChatMessages import ChatMessages, convert_chat_messages_to_request
from src.app.server.service import ChatMessageService
from src.app.utils.logger_util import log_debug

# Each incoming WebSocket message is handled via a fire-and-forget
# asyncio.create_task (see websocket_routes.py), so two messages sent for
# the SAME chat session close together can invoke the LangGraph checkpointer
# concurrently against the same thread_id, racing on its state (observed:
# duplicate/garbled final-answer messages). One lock per chat_session_id
# serializes graph invocations for that session while leaving different
# sessions fully concurrent. Module-level (not on MessageService) since a
# fresh MessageService is constructed per incoming message.
_session_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


class MessageService:
    def __init__(self):
        self.chat_message_service = ChatMessageService()

    async def save_messages(self, messages: ChatMessages):
        self.chat_message_service.save_message(request = convert_chat_messages_to_request(messages))

    async def handle_messages(self, messages: ChatMessages, session_id: str, user_id: str = None,
                              stream_handler: BaseStreamHandler = None):
        log_debug(messages)
        await self.save_messages(messages)
        lock = _session_locks[messages.chat_session_id]
        async with lock:
            await app_supervisor_graph(messages, messages.chat_session_id, stream_handler, user_id=user_id)
