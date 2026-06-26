from langchain_aws import ChatBedrockConverse

from backend.app.llm.integrations.aws.aws_inference_provider import AwsInferenceProvider
from backend.app.llm.integrations.aws.aws_model_provider import AwsModelProvider
from backend.app.llm.configuration.llm_configuration import LlmConfiguration
from backend.app.llm.configuration.model_config import ModelConfig
from backend.app.utils.logger_util import log_debug


class AwsBedrockConfiguration(LlmConfiguration):

    def __init__(self, model_config: ModelConfig, model_provider: AwsModelProvider,
                 inference_provider: AwsInferenceProvider):
        super().__init__(model_config=model_config, model_provider=model_provider,
                         inference_provider=inference_provider)

    def get_chat_llm(self):
        log_debug("getting chat llm")
        llm = ChatBedrockConverse(
            model=self.model_provider.model,
            provider=self.model_provider.model_provider,
            temperature=self.model_config.temperature,
            region_name=self.inference_provider.region_name,
            aws_access_key_id=self.inference_provider.aws_access_key,
            aws_secret_access_key=self.inference_provider.aws_secret_access_key
        )
        return llm
