import asyncio
import traceback

from fastapi import APIRouter
from langchain_core.prompts import ChatPromptTemplate
from starlette.websockets import WebSocket

from backend.app.server.messages.message_parser import parse_message
from backend.app.server.routes.message_router import MessageService
from backend.app.server.routes.websocket_stream_handler import WebsocketStreamHandler
from backend.app.utils.logger_util import log_info, log_debug

system_prompt = """
Role : You are a helpful AI assistant that provides brief, concise answers.

TOOL USAGE RULES:
1. ONLY use tools when the question CANNOT be answered from your knowledge
2. For common facts and general knowledge questions, answer directly WITHOUT mentioning tools
3. Never suggest a tool that doesn't directly answer the user's question

RESPONSE FORMAT:
- Keep answers direct
- No explanations about your thinking process

"""

websocket_router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])


@websocket_router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        log_debug(f"{session_id} : {message}")
        asyncio.create_task(handle_incoming_message(message, session_id, websocket))


async def handle_incoming_message(message: str, session_id: str, websocket: WebSocket):
    message = parse_message(message)
    try:
        message_service = MessageService()
        await message_service.handle_messages(messages=message, session_id=session_id,
                                              stream_handler=WebsocketStreamHandler(websocket))
    except Exception as e:
        log_info(f"Error during streaming: {e}")
        traceback.print_exc()
        # traceback.print_stack()
