from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.
    Defines the interface that all embedding model implementations must follow.
    """

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Returns the embedding dimension size.

        Returns:
            int: The dimension size of the embedding vectors
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """
        Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        pass

    @abstractmethod
    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Asynchronous Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        pass

    @abstractmethod
    async def aembed_query(self, text: str) -> list[float]:
        """
        Asynchronous Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        pass

