from src.app.llm.configuration.model_config import ModelConfig
from src.app.llm.integrations.anthropic.claude_llm_configurations import ClaudeLLMConfigurations
from src.app.llm.integrations.anthropic.claude_model_provider import ClaudeModelProvider
from src.app.llm.integrations.aws.aws_bedrock_configuration import AwsBedrockConfiguration
from src.app.llm.integrations.aws.aws_inference_provider import AwsInferenceProvider
from src.app.llm.integrations.aws.aws_model_provider import AwsModelProvider
from src.app.llm.integrations.azure.azure_inference_provider import AzureInferenceProvider
from src.app.llm.integrations.azure.azure_llm_configuration import AzureLLMConfiguration
from src.app.llm.integrations.azure.azure_model_provider import AzureModelProvider
from src.app.llm.integrations.gemini.gemini_llm_configurations import GeminiLlmConfigurations
from src.app.llm.integrations.gemini.gemini_model_provider import GeminiModelProvider
from src.app.llm.integrations.ollama.ollama_llm_configurations import OllamaLLMConfigurations
from src.app.llm.integrations.ollama.ollama_model_provider import OllamaModelProvider
from src.app.llm.integrations.openai.openai_llm_configuration import OpenAILLMConfiguration
from src.app.llm.integrations.openai.openai_model_provider import OpenAIModelProvider
from src.app.llm.integrations.together.together_model_provider import TogetherModelProvider
from src.app.llm.model_provider.model_provider_name import AZURE_NAME, AWS_NAME, OLLAMA_NAME, OPENAI_NAME, ANTHROPIC_NAME, \
    GOOGLE_NAME
from core.schemas.model_provider_schemas import ModelProvider
from src.app.server.service.model_provider_service import provide_model_provider_service
from src.app.utils.logger_util import log_debug


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


def get_primary_model():
    """
    Get the primary model configuration from the database.

    Returns:
        The appropriate model configuration based on the primary provider.

    Raises:
        ValueError: If no primary provider is set or provider name is not recognized.
    """
    model_config = create_model_config()
    model_provider_service = provide_model_provider_service()
    primary_provider = model_provider_service.get_primary_provider()

    if not primary_provider:
        raise ValueError("No primary provider is configured. Please set a provider as primary in the database.")

    provider_name = primary_provider.provider_name.lower()

    log_debug(f"getting {primary_provider} model")

    # Map provider names to their configuration functions
    provider_config_map = {
        AZURE_NAME.lower(): lambda: _create_azure_config_from_db(primary_provider, model_config),
        AWS_NAME.lower(): lambda: _create_aws_config_from_db(primary_provider, model_config),
        OLLAMA_NAME.lower(): lambda: _create_ollama_config_from_db(primary_provider, model_config),
        OPENAI_NAME.lower(): lambda: _create_openai_config_from_db(primary_provider, model_config),
        ANTHROPIC_NAME.lower(): lambda: _create_claude_config_from_db(primary_provider, model_config),
        GOOGLE_NAME.lower(): lambda: _create_gemini_config_from_db(primary_provider, model_config),
    }

    # Find matching provider configuration
    config_creator = provider_config_map.get(provider_name.lower())

    if not config_creator:
        raise ValueError(
            f"Unknown provider: {provider_name}. Supported providers: {', '.join(provider_config_map.keys())}")

    return config_creator()


def _create_azure_config_from_db(provider, model_config: ModelConfig):
    """Create Azure configuration from database provider."""
    return AzureLLMConfiguration(
        model_config=model_config,
        model_provider=AzureModelProvider(
            model=provider.selected_model or provider.model_list[0] if provider.model_list else None,
            api_version=provider.api_version,
        ),
        inference_provider=AzureInferenceProvider(
            endpoint=provider.base_url,
            apikey=provider.api_key,
        )
    )


def _create_aws_config_from_db(provider, model_config: ModelConfig):
    """Create AWS Bedrock configuration from database provider."""
    return AwsBedrockConfiguration(
        model_config=model_config,
        model_provider=AwsModelProvider(
            model=provider.selected_model or provider.model_list[0] if provider.model_list else None,
            model_provider=provider.model_provider,  # Using deployment_name for model_provider
        ),
        inference_provider=AwsInferenceProvider(
            region_name=provider.region,
            aws_access_key=provider.aws_access_key_id,
            aws_secret_access_key=provider.aws_secret_access_key,
        )
    )


def _create_ollama_config_from_db(provider, model_config: ModelConfig):
    """Create Ollama configuration from database provider."""
    return OllamaLLMConfigurations(
        model_config=model_config,
        model_provider=OllamaModelProvider(
            model_name=provider.selected_model or provider.model_list[0] if provider.model_list else "llama3.1:8b",
            base_url=provider.base_url,
        )
    )


# def _create_together_config_from_db(provider, model_config: ModelConfig):
#     """Create Together AI configuration from database provider."""
#     return TogetherLLMConfigurations(
#         model_config=model_config,
#         model_provider=TogetherModelProvider(
#             model_name=provider.selected_model or provider.model_list[0] if provider.model_list else None
#         ),
#         inference_provider=TogetherInferenceProvider(api_key=provider.api_key)
#     )


def _create_openai_config_from_db(provider, model_config: ModelConfig):
    """Create OpenAI configuration from database provider."""
    return OpenAILLMConfiguration(
        model_config=model_config,
        model_provider=OpenAIModelProvider(
            model_name=provider.selected_model or provider.model_list[0] if provider.model_list else None,
            api_key=provider.api_key,
        )
    )


def _create_claude_config_from_db(provider, model_config: ModelConfig):
    """Create Claude/Anthropic configuration from database provider."""
    return ClaudeLLMConfigurations(
        model_config=model_config,
        model_provider=ClaudeModelProvider(
            model_name=provider.selected_model or provider.model_list[0] if provider.model_list else None,
            api_key=provider.api_key,
        )
    )


def _create_gemini_config_from_db(provider, model_config: ModelConfig):
    """Create Gemini/Google configuration from database provider."""
    return GeminiLlmConfigurations(
        model_config=model_config,
        model_provider=GeminiModelProvider(
            model_name=provider.selected_model or provider.model_list[0] if provider.model_list else None,
            api_key=provider.api_key,
        )
    )
