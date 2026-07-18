from llm_module.model_provider.model_provider import ModelProvider


class ClaudeModelProvider(ModelProvider):

    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name=model_name)
        self.model_name = model_name
        self.api_key = api_key
