import os

from backend.app.llm.configuration.embedding_configuration import EmbeddingConfiguration
from core.utils.constants import ModelProviderName, InferenceProviderName
from backend.app.utils.env_util import load_environment
from core.utils.file_util import get_embedding_models_path
from backend.app.utils.logger_util import log_debug


def _get_embedding_config(model_name: str = "embeddinggemma:latest",
                         api_key: str = None,
                         endpoint: str = None,
                         api_version: str = None,
                         dimension: int = 768):
    """
    Create an embedding configuration with specified parameters.

    Args:
        model_name: Name of the embedding model
        api_key: API key for the service
        endpoint: API endpoint URL
        api_version: API version
        dimension: Embedding dimension size

    Returns:
        EmbeddingConfiguration: Configured embedding configuration object
    """
    return EmbeddingConfiguration(
        model_name=model_name,
        api_key=api_key,
        endpoint=endpoint,
        api_version=api_version,
        dimension=dimension,
        model_provider=ModelProviderName.GOOGLE,
    )


def _get_openai_embeddings():
    from backend.app.llm.embeddings.embedding_factory import create_embedding_model

    # load_environment("environment/.env.openai")
    load_environment("../environment/.env.openai")
    key = os.getenv("OPENAI_API_KEY")
    log_debug(f"OpenAI API Key loaded: {key}")
    config = EmbeddingConfiguration(
        model_name="text-embedding-3-small",
        api_key=key,
        dimension=1536,
        model_provider=ModelProviderName.OPENAI,
        inference_provider=InferenceProviderName.OPENAI
    )
    return create_embedding_model(config)


def _get_azure_embeddings():
    from backend.app.llm.embeddings.embedding_factory import create_embedding_model

    load_environment("environment/.env.azure")
    config = EmbeddingConfiguration(
        model_name="text-embedding-3-large",
        endpoint=os.getenv("ENDPOINT"),
        api_key=os.getenv("API_KEY"),
        api_version=os.getenv("API_VERSION"),
        dimension=3072,
        model_provider=ModelProviderName.OPENAI,
        inference_provider=InferenceProviderName.AZURE
    )
    return create_embedding_model(config)


def _create_ollama_embedding_model():
    """
       Create an embedding model using Ollama.

       Returns:
           AppEmbeddingModel: An instance of AppEmbeddingModel configured for Ollama.
       """
    from backend.app.llm.embeddings.embedding_factory import create_embedding_model

    config = EmbeddingConfiguration(
        model_name="embeddinggemma:latest",
        dimension=768,
        model_provider=ModelProviderName.OLLAMA,
        inference_provider=InferenceProviderName.OLLAMA
    )
    return create_embedding_model(config)


def create_sentence_transformer_embedding_model(model_name: str = str(get_embedding_models_path()), dimension: int = 384):
    """
    Create an embedding model using SentenceTransformer.

    Args:
        model_name: Name of the SentenceTransformer model
        dimension: Embedding dimension size (default 384 for all-MiniLM-L6-v2)

    Returns:
        AppEmbeddingModel: An instance of AppEmbeddingModel configured for SentenceTransformer.
    """
    from backend.app.llm.embeddings.embedding_factory import create_embedding_model

    config = EmbeddingConfiguration(
        model_name=model_name,
        dimension=dimension,
        model_provider=ModelProviderName.HUGGINGFACE,
        inference_provider=InferenceProviderName.HUGGINGFACE
    )
    return create_embedding_model(config)


def create_default_embedding_model():
    """
    Create a default embedding model using Ollama.

    Returns:
        AppEmbeddingModel: An instance of AppEmbeddingModel configured for Ollama.
    """
    return create_sentence_transformer_embedding_model()
    # return _create_ollama_embedding_model()
    # return _get_openai_embeddings()
