from fastapi import APIRouter

from backend.app.server.database.settings_repository import SettingsRepository
from backend.app.server.service.settings_service import provide_settings_service

settings_routes = APIRouter(
    tags=["api"],
)

settings_repository = SettingsRepository()
settings_service = provide_settings_service(settings_repository)

@settings_routes.get(path="/settings/models")
def get_all_model_providers():
    return settings_service.get_model_providers()