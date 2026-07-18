import mimetypes
import traceback
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, Form
from langchain_core.messages import HumanMessage
from starlette.responses import FileResponse

from agents.persistence.database_check_pointer import provide_checkpointer
from rag.factory.rag_pipeline_factory import RagPipelineFactory
from src.app.server.messages.ChatMessages import create_chat_message, ContentType, convert_chat_messages_to_request, ASSISTANT, \
    AgentMode
from src.app.server.processor.upload_file_handler import UploadFileHandler
from src.app.server.schemas import ChatSessionCreateRequest
from src.app.server.service.chat_message_service import get_chat_message_service
from src.app.server.service.chat_session_service import provide_chat_session_service
from core.utils.file_util import get_install_root
from src.app.utils.logger_util import log_error, log_info, log_debug
from src.app.utils.message_util import add_messages_to_graph, get_session_config
from core.utils.time_util import get_utc_time

file_uploader = UploadFileHandler()
session_service = provide_chat_session_service()
message_service = get_chat_message_service()
api_routes = APIRouter(
    tags=["api"],
)


@api_routes.post("/create_files/")
async def create_file(file: UploadFile):
    # Create directory if it doesn't exist
    upload_dir = Path("../data/files")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Create file path
    file_path = upload_dir / file.filename
    return {"file_path": str(file_path)}


async def save_file_upload_message(file_name: str, file_path: str, mime_type: str, session_id: str,
                                   user_id: str = None):
    message_id = message_service.generate_chat_message_id()
    utc_time = get_utc_time()
    message = create_chat_message(
        messages=file_name,  # Just the file name as the message text
        chat_session_id=session_id,
        sender=user_id,
        receiver=ASSISTANT,
        content_type=ContentType.FILE,
        message_id=message_id,
        chat_mode=AgentMode.AGENT,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type,
        utc_time=utc_time,
    )
    message_request = convert_chat_messages_to_request(message)
    message_service.save_message(request=message_request)


@api_routes.post("/uploadfile")
async def upload_file(file: UploadFile, session_id: str = Form(...), user_id: str = Form(None)):
    try:
        # Validate session_id
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")

        log_info(f"session_id received in upload file: {session_id} user id {user_id}")
        response = await file_uploader.upload_file(file=file)
        rag_pipeline = RagPipelineFactory.create_rag_pipeline(response.path)
        await rag_pipeline.start(session_id=session_id, user_id=user_id)
        await add_doc_message(session_id=session_id, user_id=user_id, file_metadata=response)
        await save_file_upload_message(
            response.file_name,
            file_path=response.path,
            mime_type=response.mime_type,
            session_id=session_id,
            user_id=user_id,
        )
        return response
    except Exception as e:
        log_error(str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        await file.close()


@api_routes.get("/files/download")
async def download_file_by_query(file_path: str):
    """
    Download file using query parameter.

    Example: GET /files/download?file_path=documents/report.pdf
    """
    base_path = get_install_root()
    file_location = base_path / "data/files" / file_path

    mime_type, _ = mimetypes.guess_type(str(file_location))
    response = FileResponse(
        path=str(file_location),
        media_type=mime_type or "application/octet-stream",
        filename=file_location.name
    )
    log_debug(file_location)
    log_debug(mime_type)
    return response


async def add_doc_message(session_id, user_id, file_metadata):
    if not session_service.session_exist(session_id):
        request = ChatSessionCreateRequest(user_id=user_id, title="")
        await session_service.create_chat_session(request=request)
    message = HumanMessage(
        content=f"I have uploaded a document and file metadata is {file_metadata}",
        additional_kwargs={
            "file_metadata": file_metadata
        }
    )
    await add_messages_to_graph(session_id=session_id, message=message)


async def fetch_state(session_id: str):
    async with provide_checkpointer() as checkpointer:
        session_config = get_session_config(session_id)
        checkpoint = await checkpointer.aget_tuple(session_config)
        state = checkpoint
        print(state)
