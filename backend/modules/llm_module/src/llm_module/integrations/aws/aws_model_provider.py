from llm_module.model_provider.model_provider import ModelProvider


class AwsModelProvider(ModelProvider):

    def __init__(self, model: str, model_provider: str):
        self.model = model
        self.model_provider = model_provider
