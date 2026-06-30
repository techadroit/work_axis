import asyncio
import multiprocessing
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.app.llm.model_downloader import download_embedding_model
from src.app.server.database.db_session import initialize_database
from src.app.server.routes.chat_api_routes import chat_api_router
from src.app.server.routes.chat_session_api_routes import chat_session_api_router
from src.app.server.routes.file_api_routes import api_routes
from src.app.server.routes.login_api_routes import login_api_routes
from src.app.server.routes.logs_sse_routes import logs_sse_router
from src.app.server.routes.model_provider_routes import model_provider_routes
from src.app.server.routes.settings_routes import settings_routes
from src.app.server.routes.user_api_routes import user_api_router
from src.app.server.routes.websocket_routes import websocket_router
from src.app.utils.logger_util import log_info


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and SSL
    log_info("Starting up application...")
    initialize_database()
    # Run embedding-model download in a background thread so startup is non-blocking
    asyncio.create_task(asyncio.to_thread(download_embedding_model))

    # Configure SSL for external API calls
    # try:
    #     from utils.http_client_util import configure_ssl_for_apis
    #     configure_ssl_for_apis()
    # except Exception as e:
    #     log_info(f"SSL configuration info: {e}")
    #
    yield
    # Shutdown: cleanup if needed
    log_info("Shutting down application...")


pi_app = FastAPI(lifespan=lifespan)

# Configure CORS
pi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

pi_app.include_router(websocket_router)
# API routers (all with /api prefix)
api_routers = [api_routes, login_api_routes, chat_session_api_router, user_api_router, chat_api_router, settings_routes, model_provider_routes,logs_sse_router]
for router in api_routers:
    pi_app.include_router(router, prefix="/api")


@pi_app.get("/health", tags=["health"])
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})


def main():
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(pi_app, host=host, port=port, log_level="info")

if __name__ == '__main__':
    main()

