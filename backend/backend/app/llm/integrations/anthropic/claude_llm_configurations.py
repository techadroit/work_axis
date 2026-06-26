from langchain_anthropic import ChatAnthropic

from backend.app.llm.integrations.anthropic.claude_model_provider import ClaudeModelProvider
from backend.app.llm.configuration.llm_configuration import LlmConfiguration
from backend.app.llm.configuration.model_config import ModelConfig


class ClaudeLLMConfigurations(LlmConfiguration):

    def __init__(self, model_config: ModelConfig, model_provider: ClaudeModelProvider):
        super().__init__(model_config, model_provider)
        self._chat_llm = ChatAnthropic(
            model=self.model_provider.model_name,
            api_key=self.model_provider.api_key,
            temperature=model_config.temperature,
            max_retries=model_config.max_retries,
            max_tokens=model_config.max_tokens,
            timeout=model_config.timeout
        )

    def get_chat_llm(self):
        return self._chat_llm
