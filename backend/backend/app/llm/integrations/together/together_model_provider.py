from backend.app.llm.model_provider.model_provider import ModelProvider


class TogetherModelProvider(ModelProvider):
    def __init__(self, model_name: str):
        super().__init__(model_name=model_name)
        self.model_name = model_name