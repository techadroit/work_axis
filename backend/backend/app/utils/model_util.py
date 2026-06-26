import os

from backend.app.llm.configuration.model_config import ModelConfig
from backend.app.llm.model_provider.model_provider_factory import get_primary_model
from backend.app.server.service.model_provider_service import provide_model_provider_service
from backend.app.utils.env_util import load_environment
from backend.app.utils.logger_util import log_debug


def create_model_config(temperature: float = 0.7, top_p: float = 0.9, max_retries: int = 3) -> ModelConfig:
    """
    Create a ModelConfig instance with specified parameters.

    Args:
        temperature (float): The temperature setting for the model.
        top_p (float): The top-p setting for the model.
        max_retries (int): The maximum number of retries for model requests.

    Returns:
        ModelConfig: An instance of ModelConfig with the specified settings.
    """
    return ModelConfig(temperature=temperature, top_p=top_p, max_retries=max_retries)


def create_azure_config(model_config: ModelConfig = create_model_config()):
    load_environment('environment/.env.azure')
    from backend.app.llm.integrations.azure.azure_inference_provider import AzureInferenceProvider
    from backend.app.llm.integrations.azure.azure_llm_configuration import AzureLLMConfiguration
    from backend.app.llm.integrations.azure.azure_model_provider import AzureModelProvider
    return AzureLLMConfiguration(
        model_config=model_config,
        model_provider=AzureModelProvider(
            model=os.getenv("MODEL_NAME"),
            api_version=os.getenv("API_VERSION"),
        ),
        inference_provider=AzureInferenceProvider(
            endpoint=os.getenv("ENDPOINT"),
            apikey=os.getenv("API_KEY"),
        )
    )


def create_aws_bedrock_config(model_config: ModelConfig = create_model_config()):
    load_environment('environment/.env.aws')
    from backend.app.llm.integrations.aws.aws_bedrock_configuration import AwsBedrockConfiguration
    from backend.app.llm.integrations.aws.aws_model_provider import AwsModelProvider
    from backend.app.llm.integrations.aws.aws_inference_provider import AwsInferenceProvider
    return AwsBedrockConfiguration(
        model_config=model_config,
        model_provider=AwsModelProvider(
            model=os.getenv("MODEL_NAME"),
            model_provider=os.getenv("MODEL_PROVIDER"),
        ),
        inference_provider=AwsInferenceProvider(
            region_name=os.getenv("REGION_NAME"),
            aws_access_key=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    )


def create_ollama_config(model_config: ModelConfig = create_model_config()):
    from backend.app.llm.integrations.ollama.ollama_llm_configurations import OllamaLLMConfigurations
    from backend.app.llm.integrations.ollama.ollama_model_provider import OllamaModelProvider

    return OllamaLLMConfigurations(model_config=model_config, model_provider=OllamaModelProvider(
        model_name="llama3.1:8b"
    ))


def create_together_config(model_config: ModelConfig = create_model_config()):
    from backend.app.llm.integrations.together.together_llm_configurations import TogetherLLMConfigurations
    from backend.app.llm.integrations.together.together_model_provider import TogetherModelProvider
    from backend.app.llm.integrations.together.together_inference_provider import TogetherInferenceProvider
    load_environment(f'environment/.env.together')
    return TogetherLLMConfigurations(model_config=model_config,
                                     model_provider=TogetherModelProvider(model_name=os.getenv("MODEL_NAME")),
                                     inference_provider=TogetherInferenceProvider(api_key=os.getenv("API_KEY")))


def create_openai_config(model_config: ModelConfig = create_model_config()):
    from backend.app.llm.integrations.openai.openai_llm_configuration import OpenAILLMConfiguration
    from backend.app.llm.integrations.openai.openai_model_provider import OpenAIModelProvider
    load_environment('environment/.env.openai')
    return OpenAILLMConfiguration(
        model_config=model_config,
        model_provider=OpenAIModelProvider(
            model_name=os.getenv("MODEL_NAME"),
            api_key=os.getenv("API_KEY"),
        )
    )


def create_claude_config(model_config: ModelConfig = create_model_config()):
    from backend.app.llm.integrations.anthropic.claude_llm_configurations import ClaudeLLMConfigurations
    from backend.app.llm.integrations.anthropic.claude_model_provider import ClaudeModelProvider
    load_environment('environment/.env.anthropic')
    return ClaudeLLMConfigurations(
        model_config=model_config,
        model_provider=ClaudeModelProvider(
            model_name=os.getenv("MODEL_NAME"),
            api_key=os.getenv("API_KEY"),
        )
    )


def create_gemini_config(model_config: ModelConfig = create_model_config()):
    from backend.app.llm.integrations.gemini.gemini_llm_configurations import GeminiLlmConfigurations
    from backend.app.llm.integrations.gemini.gemini_model_provider import GeminiModelProvider
    load_environment('environment/.env.gemini')
    return GeminiLlmConfigurations(
        model_config=model_config,
        model_provider=GeminiModelProvider(
            model_name=os.getenv("MODEL_NAME"),
            api_key=os.getenv("API_KEY"),
        )
    )


def get_default_model_config():
    return get_primary_model()
    # return create_ollama_config()
    # return create_openai_config()
    # return create_azure_config()
    # return create_aws_bedrock_config()

# log_debug(get_default_model_config())