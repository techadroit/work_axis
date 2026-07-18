from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from llm_module.configuration.llm_configuration import LlmConfiguration
from llm_module.configuration.model_config import ModelConfig
from llm_module.integrations.azure.azure_model_provider import AzureModelProvider
from llm_module.integrations.azure.azure_inference_provider import AzureInferenceProvider


class AzureLLMConfiguration(LlmConfiguration):

    def __init__(self, model_config: ModelConfig, model_provider: AzureModelProvider,
                 inference_provider: AzureInferenceProvider):
        super().__init__(model_config, model_provider, inference_provider)
        self._chat_llm = AzureChatOpenAI(
            azure_endpoint=self.inference_provider.endpoint,
            api_key=self.inference_provider.apikey,
            model=self.model_provider.model,
            api_version=self.model_provider.api_version,
            temperature=self.model_config.temperature,
            max_tokens=self.model_config.max_tokens,
            timeout=self.model_config.timeout,
            max_retries=self.model_config.max_retries,
        )

    def get_chat_llm(self) -> BaseChatModel:
        return self._chat_llm