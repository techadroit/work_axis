from langchain_core.messages import AIMessageChunk, AIMessage
from starlette.websockets import WebSocketState

from src.app.server.base.base_stream_handler import BaseStreamHandler
from src.app.server.cache.message_cache import get_message_cache
from src.app.server.messages.ChatMessages import create_chat_message, ChatMessages, convert_chat_messages_to_request, \
    MessageType
from src.app.server.schemas import ChatSessionUpdateRequest
from src.app.server.service import ChatMessageService, ChatSessionService
from src.app.utils.logger_util import log_debug, log_error, log_response
from core.utils.time_util import utc_now_iso


class WebsocketStreamHandler(BaseStreamHandler):
    keys = dict[str, str]()

    def __init__(self, websocket):
        self.websocket = websocket
        self.chat_message_service = ChatMessageService()
        self.chat_session_service = ChatSessionService()
        self.message_cache = get_message_cache()

    async def handle_stream(self, stream, **kwargs):
        # Stream format: ((), 'stream_type', data)
        stream_type = stream[1]

        # Only process 'messages' type streams
        if stream_type == "messages":
            # log_debug(stream)
            await self.process_message_stream(stream, kwargs)
        elif stream_type == "updates":
            # log_debug(stream)
            await self.process_updates_stream(stream, kwargs)  # Handle updates if needed

    async def process_message_stream(self, stream, kwargs):
        # Extract AIMessageChunk, AIMessage and metadata
        log_response(stream)
        message = stream[2][0]  # AIMessageChunk object
        metadata = stream[2][1]  # Dictionary with langgraph metadata

        if isinstance(message, AIMessage) or isinstance(message, AIMessageChunk):
            node_name = metadata.get("langgraph_node")
            emitting_node = kwargs.pop("emitting_node", None)
            chat_session_id = kwargs.get("chat_session_id")
            if node_name in emitting_node:
                stream_id = message.id
                if stream_id not in self.keys:
                    self.keys[stream_id] = self.chat_message_service.generate_chat_message_id()
                msg_id = self.keys[stream_id]
                time = utc_now_iso()
                chat_message = create_chat_message(messages=message.content, chat_session_id=chat_session_id,
                                                   message_id=msg_id,utc_time=time)
                chat_message_str = chat_message.model_dump_json()
                if isinstance(message, AIMessageChunk):
                    if self.websocket.client_state == WebSocketState.CONNECTED:
                        await self.websocket.send_text(chat_message_str)
                elif isinstance(message, AIMessage):
                    self._save_to_db(chat_message)

    async def process_updates_stream(self, stream, kwargs):
        # Placeholder for processing updates stream if needed
        updates = stream[2]
        if "title_generation_node" in updates:
            title_data = updates["title_generation_node"]
            if title_data:
                chat_title = title_data.get("chat_title")
                if chat_title:
                    log_debug(f"Generated chat title: {chat_title}")
                    chat_session_id = kwargs.get("chat_session_id")
                    if chat_session_id:
                        await self._save_chat_title(chat_session_id, chat_title)
                    msg_id = self.chat_message_service.generate_chat_message_id()
                    utc_time = utc_now_iso()
                    chat_message = create_chat_message(messages=chat_title, chat_session_id=chat_session_id,
                                                       message_id=msg_id, message_type=MessageType.UPDATE_TITLE,
                                                       utc_time=utc_time)
                    message = chat_message.model_dump_json()
                    log_response(message)
                    await self.websocket.send_text(message)

    async def _save_chat_title(self, chat_session_id: str, title: str):
        """Save the generated chat title to the database."""
        try:
            # Assuming you have a method to update chat session title
            # Replace with your actual implementation
            await self.chat_session_service.update_chat_session(chat_session_id,
                                                                request=ChatSessionUpdateRequest(title=title,
                                                                                                 is_archived=None))
        except Exception as e:
            log_error(f"Error saving chat title for session {chat_session_id} {e} ")

    def _save_to_cache(self, message: ChatMessages):
        self.message_cache.add_or_update(message.message_id, message)

    def _save_to_db(self, message):
        log_debug("Message Stream complete:")
        # msg = self.message_cache.get_message(message.message_id)
        # self.message_cache.remove_message(message.message_id)
        try:
            log_debug(message)
            request = convert_chat_messages_to_request(message)
            self.chat_message_service.save_message(request)
        except Exception as e:
            log_error(f"error in saving message to db: {request}  {e} ")
