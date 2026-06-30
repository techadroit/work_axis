from typing import List
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

from src.app.llm.embeddings.app_embedding_model import AppEmbeddingModel
from src.app.llm.embeddings.embedding_model import EmbeddingModel


class SentenceTransformerEmbeddings(AppEmbeddingModel):
    """
    Wrapper for SentenceTransformer to make it compatible with LangChain's Embeddings interface.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the SentenceTransformer model.

        Args:
            model_name: Name or path of the SentenceTransformer model
        """
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings as lists of floats.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding as a list of floats.
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Asynchronous Embed search docs.

        Args:
            texts: List of text to embed.

        Returns:
            List of embeddings.
        """
        # SentenceTransformer doesn't have native async support, so we just call the sync version
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> List[float]:
        """
        Asynchronous Embed query text.

        Args:
            text: Text to embed.

        Returns:
            Embedding.
        """
        # SentenceTransformer doesn't have native async support, so we just call the sync version
        return self.embed_query(text)

