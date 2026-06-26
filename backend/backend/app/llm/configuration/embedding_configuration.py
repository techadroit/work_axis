from core.utils.constants import ModelProviderName, InferenceProviderName


class EmbeddingConfiguration:
    def __init__(self,
                 model_name: str = "embeddinggemma:latest",
                 api_key: str = None,
                 endpoint: str = None,
                 api_version: str = None,
                 dimension: int = None,
                 model_provider: str = ModelProviderName.OLLAMA,
                 inference_provider: str = InferenceProviderName.OLLAMA):
        self.model_name = model_name
        self.api_key = api_key
        self.endpoint = endpoint
        self.api_version = api_version
        self.dimension = dimension
        self.model_provider = model_provider
        self.inference_provider = inference_provider

    def get_dimension(self):
        return self.dimension

    def get_model_name(self):
        return self.model_name

    def get_api_key(self):
        return self.api_key

    def get_endpoint(self):
        return self.endpoint

    def get_api_version(self):
        return self.api_version

    def get_model_provider(self):
        return self.model_provider

    def get_inference_provider(self):
        return self.inference_provider

    def get_dimension(self):
        return self.dimension
