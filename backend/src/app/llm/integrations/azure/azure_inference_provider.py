from src.app.llm.inference_provider.inference_provider import InferenceProvider

class AzureInferenceProvider(InferenceProvider):
    def __init__(self, endpoint: str, apikey: str):
        self.endpoint = endpoint
        self.apikey = apikey

