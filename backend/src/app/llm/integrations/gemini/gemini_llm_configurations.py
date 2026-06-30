from langchain_google_genai import ChatGoogleGenerativeAI

from src.app.llm.configuration.llm_configuration import LlmConfiguration
from src.app.llm.configuration.model_config import ModelConfig
from src.app.llm.model_provider.model_provider import ModelProvider


class GeminiLlmConfigurations(LlmConfiguration):

    def __init__(self, model_config: ModelConfig, model_provider: ModelProvider = None):
        super().__init__(model_provider)
        self.model_provider = model_provider
        self._chat_llm = ChatGoogleGenerativeAI(
            model=model_provider.model_name,
            google_api_key=model_provider.api_key,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            timeout=model_config.timeout,
            max_retries=model_config.max_retries,
        )

    def get_chat_llm(self):
        return self._chat_llm
