from langchain_openai import ChatOpenAI

from src.app.llm.integrations.openai.openai_model_provider import OpenAIModelProvider
from src.app.llm.configuration.llm_configuration import LlmConfiguration
from src.app.llm.configuration.model_config import ModelConfig


class OpenAILLMConfiguration(LlmConfiguration):
    def __init__(self, model_config: ModelConfig, model_provider: OpenAIModelProvider):
        super().__init__(model_config, model_provider, inference_provider=None)

        self._chat_llm = ChatOpenAI(
            api_key=self.model_provider.api_key,
            model=self.model_provider.model_name,
            temperature=self.model_config.temperature,
            max_tokens=self.model_config.max_tokens,
            timeout=self.model_config.timeout,
            max_retries=self.model_config.max_retries,
        )

    def get_chat_llm(self):
        return self._chat_llm
