from langchain_core.embeddings import Embeddings

from backend.app.llm.embeddings.embedding_model import EmbeddingModel


class AppEmbeddingModel(EmbeddingModel):
    """
    Adapter class for LangChain embedding models.
    Acts as a wrapper that delegates all embedding operations to the underlying model.

    Args:
        embedding_model: A LangChain Embeddings instance (e.g., OllamaEmbeddings, OpenAIEmbeddings)
        dimension: The dimension size of the embedding vectors
    """

    def __init__(self, embedding_model: Embeddings, dimension: int = 768):
        self.embedding_model = embedding_model
        self.dimension = dimension

    def get_embedding(self) -> Embeddings:
        """
        Returns the embedding model instance.

        Returns:
            Embeddings: The LangChain embedding model
        """
        return self.embedding_model

    def get_dimension(self) -> int:
        """
        Returns the embedding dimension size.

        Returns:
            int: The dimension size of the embedding vectors
        """
        return self.dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        return self.embedding_model.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        """
        Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        return self.embedding_model.embed_query(text)

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Asynchronous Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        return await self.embedding_model.aembed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        """
        Asynchronous Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        return await self.embedding_model.aembed_query(text)

