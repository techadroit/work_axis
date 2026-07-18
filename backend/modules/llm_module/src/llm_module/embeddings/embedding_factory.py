from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings, AzureOpenAIEmbeddings

from llm_module.configuration.embedding_configuration import EmbeddingConfiguration
from llm_module.embeddings.app_embedding_model import AppEmbeddingModel
from llm_module.embeddings.sentence_transformer_embeddings import SentenceTransformerEmbeddings
from core.utils.constants import ModelProviderName, InferenceProviderName
from core.utils.logger_util import log_debug


def create_embedding_model(config: EmbeddingConfiguration) -> AppEmbeddingModel:
    """
    Factory function to create an AppEmbeddingModel from EmbeddingConfiguration.

    Args:
        config: EmbeddingConfiguration instance containing model parameters

    Returns:
        AppEmbeddingModel: Configured embedding model wrapper
    """
    embedding_model = None
    inference_provider = config.get_inference_provider().lower()
    model_provider = config.get_model_provider().lower()

    # Determine which embedding provider to use based on inference_provider
    if inference_provider == InferenceProviderName.AZURE:
        # Azure OpenAI based on model_provider
        if model_provider == ModelProviderName.OPENAI:
            embedding_model = AzureOpenAIEmbeddings(
                model=config.get_model_name(),
                azure_endpoint=config.get_endpoint(),
                api_key=config.get_api_key(),
                api_version=config.get_api_version(),
            )
        else:
            raise ValueError(f"Unsupported model_provider '{model_provider}' for inference_provider 'azure'")

    elif inference_provider == InferenceProviderName.OPENAI:
        # OpenAI based on model_provider
        log_debug(f"Creating OpenAIEmbeddings model for inference_provider '{config.get_api_key()} {config.get_model_name()}'")
        embedding_model = OpenAIEmbeddings(
            model=config.get_model_name(),
            api_key=config.get_api_key(),
        )

    elif inference_provider == InferenceProviderName.OLLAMA:
        # Ollama based on model_provider
        if model_provider == ModelProviderName.OLLAMA:
            embedding_model = OllamaEmbeddings(
                model=config.get_model_name()
            )
        else:
            raise ValueError(f"Unsupported model_provider '{model_provider}' for inference_provider 'ollama'")

    elif inference_provider == InferenceProviderName.HUGGINGFACE:
        # HuggingFace SentenceTransformer
        if model_provider == ModelProviderName.HUGGINGFACE:
            embedding_model = SentenceTransformerEmbeddings(
                model_name=config.get_model_name()
            )
        else:
            raise ValueError(f"Unsupported model_provider '{model_provider}' for inference_provider 'huggingface'")

    else:
        raise ValueError(f"Unsupported inference_provider: {inference_provider}")

    # Wrap in AppEmbeddingModel with dimension from config
    return AppEmbeddingModel(
        embedding_model=embedding_model,
        dimension=config.get_dimension()
    )
