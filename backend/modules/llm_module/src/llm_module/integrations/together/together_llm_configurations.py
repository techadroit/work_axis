from langchain_together import ChatTogether

from llm_module.integrations.together.together_inference_provider import TogetherInferenceProvider
from llm_module.integrations.together.together_model_provider import TogetherModelProvider
from llm_module.configuration.llm_configuration import LlmConfiguration
from llm_module.configuration.model_config import ModelConfig


class TogetherLLMConfigurations(LlmConfiguration):

    def __init__(self, model_config: ModelConfig, model_provider: TogetherModelProvider,
                 inference_provider=TogetherInferenceProvider):
        super().__init__(model_config=model_config, model_provider=model_provider,
                         inference_provider=inference_provider)

    def get_chat_llm(self):
        self._chat_llm = ChatTogether(
            together_api_key=self.inference_provider.api_key,
            model=self.model_provider.model_name,
            temperature=self.model_config.temperature
        )
        return self._chat_llm
