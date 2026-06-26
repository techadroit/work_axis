from fastapi import APIRouter, HTTPException

from backend.app.server.config.app_config import get_app_config
from backend.app.server.service import ChatMessageService
from backend.app.utils.logger_util import log_info

app_config = get_app_config()

chat_api_router = APIRouter(
    prefix="/messages",
)

chat_message_service = ChatMessageService()


# ========== Chat CRUD Endpoints ==========

# @chat_api_router.post("/create")
# def create_chat(chat_create: ChatCreate):
#     """Create a new chat session"""
#     try:
#         chat_id = ChatMessageService.save_message(chat_create)
#         return {"chat_id": chat_id, "message": "Chat created successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@chat_api_router.get("/{chat_session_Id}")
def get_chat(chat_session_Id: str, page_no: int = 0, page_size: int = app_config.DEFAULT_PAGE_SIZE):
    """Get a specific chat by ID"""
    log_info(chat_session_Id)
    chat = chat_message_service.get_messages_by_chat_session(chat_session_id=chat_session_Id, page_size=page_size,
                                                             page=page_no)
    log_info(chat)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


# @chat_api_router.get("/users/{user_id}/messages")
# def get_user_chats(user_id: str, include_archived: bool = False):
#     """Get all chats for a user"""
#     chats = chat_message_service.get_messages_by_chat_session(user_id, include_archived)
#     return {"chats": chats, "count": len(chats)}


# @chat_api_router.put("/{chat_session_Id}")
# def update_chat(chat_session_Id: str, chat_update: ChatUpdate):
#     """Update chat"""
#     success = ChatSessionRepository.update_chat(chat_session_Id, chat_update)
#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to update chat")
#     return {"message": "Chat updated successfully"}


# @chat_api_router.put("/{chat_id}/archive")
# def archive_chat(chat_id: str):
#     """Archive a chat"""
#     success = ChatSessionRepository.archive_chat(chat_id)
#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to archive chat")
#     return {"message": "Chat archived successfully"}


@chat_api_router.delete("/{message_id}")
def delete_chat(message_id: str):
    """Permanently delete a chat and all its messages"""
    success = chat_message_service.delete_message(message_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete chat")
    return {"message": "Chat deleted successfully"}
