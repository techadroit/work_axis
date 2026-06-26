from backend.app.llm.inference_provider.inference_provider import InferenceProvider

class TogetherInferenceProvider(InferenceProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
