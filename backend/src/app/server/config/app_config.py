class AppConfig:
    DEBUG = True
    MAX_MESSAGE_LENGTH = 20
    DEFAULT_PAGE_SIZE = 20

def get_app_config() -> AppConfig:
    return AppConfig()