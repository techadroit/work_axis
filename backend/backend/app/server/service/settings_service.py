from backend.app.server.database.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, settings_repository: SettingsRepository):
        self.settings_repository = settings_repository

    def get_model_providers(self):
        return self.settings_repository.get_all_model_providers()


def provide_settings_service(settings_repository):
    return SettingsService(settings_repository)