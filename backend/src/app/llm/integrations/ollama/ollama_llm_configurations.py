from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
import os

from src.app.llm.configuration.llm_configuration import LlmConfiguration
from src.app.llm.configuration.model_config import ModelConfig
from src.app.llm.model_provider.model_provider import ModelProvider


class OllamaLLMConfigurations(LlmConfiguration):

    def __init__(self, model_config: ModelConfig, model_provider: ModelProvider = None, inference_provider=None):
        super().__init__(model_config, model_provider, inference_provider)

    def get_chat_llm(self) -> BaseChatModel:
        base_url = getattr(self.model_provider, "base_url", None) or os.getenv("OLLAMA_BASE_URL")

        # Inside containers, localhost points to the container itself, not the host where Ollama may be running.
        if base_url and os.path.exists("/.dockerenv"):
            base_url = base_url.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")

        self._chat_llm = ChatOllama(
            model=self.model_provider.model_name,
            temperature=self.model_config.temperature,
            reasoning=False,
            base_url=base_url,
        )
        return self._chat_llm
