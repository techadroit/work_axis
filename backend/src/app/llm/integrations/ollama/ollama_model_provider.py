from src.app.llm.model_provider.model_provider import ModelProvider


class OllamaModelProvider(ModelProvider):
    def __init__(self, model_name: str, base_url: str | None = None):
        self.model_name = model_name
        self.base_url = base_url