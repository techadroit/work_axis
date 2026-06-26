from fastapi import APIRouter, HTTPException

from backend.app.server.service.chat_session_service import ChatSessionService
from backend.app.server.schemas.chat_session_schemas import (
    ChatSessionCreateRequest, ChatSessionUpdateRequest,
    ChatSessionCreateResponse, ChatSessionResponse,
    ChatSessionListResponse, OperationResponse
)

chat_session_api_router = APIRouter(
    prefix="/chat",
)

# Initialize service layer
chat_session_service = ChatSessionService()


# ========== Chat Session CRUD Endpoints ==========

@chat_session_api_router.post("/sessions", response_model=ChatSessionCreateResponse)
async def create_chat_session(request: ChatSessionCreateRequest):
    """Create a new chat session"""
    try:
        response = await chat_session_service.create_chat_session(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chat_session_api_router.get("/sessions/{chat_session_id}", response_model=ChatSessionResponse)
def get_chat_session(chat_session_id: str):
    """Get a specific chat session by ID"""
    chat_session = chat_session_service.get_chat_session_by_id(chat_session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return chat_session


@chat_session_api_router.get("/users/{user_id}/sessions", response_model=ChatSessionListResponse)
def get_user_chat_sessions(user_id: str, include_archived: bool = False):
    """Get all chat sessions for a user"""
    response = chat_session_service.get_chat_sessions_by_user(user_id, include_archived)
    return response


@chat_session_api_router.put("/sessions/{chat_session_id}", response_model=OperationResponse)
def update_chat_session(chat_session_id: str, request: ChatSessionUpdateRequest):
    """Update chat session"""
    response = chat_session_service.update_chat_session(chat_session_id, request)
    if not response.success:
        raise HTTPException(status_code=404 if "not found" in response.message else 500, detail=response.message)
    return response


@chat_session_api_router.put("/sessions/{chat_session_id}/archive", response_model=OperationResponse)
def archive_chat_session(chat_session_id: str):
    """Archive a chat session"""
    response = chat_session_service.archive_chat_session(chat_session_id)
    if not response.success:
        raise HTTPException(status_code=404 if "not found" in response.message else 500, detail=response.message)
    return response


@chat_session_api_router.delete("/sessions/{chat_session_id}", response_model=OperationResponse)
def delete_chat_session(chat_session_id: str):
    """Permanently delete a chat session and all its messages"""
    response = chat_session_service.delete_chat_session(chat_session_id)
    if not response.success:
        raise HTTPException(status_code=404 if "not found" in response.message else 500, detail=response.message)
    return response

