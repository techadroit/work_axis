from llm_module.model_provider.model_provider import ModelProvider

class AzureModelProvider(ModelProvider):
    def __init__(self, model: str, api_version: str):
        self.model = model
        self.api_version = api_version

