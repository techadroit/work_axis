from backend.app.vector_db.base.vector_db_client import VectorDbClient
from backend.app.vector_db.integrations.chroma_vector_db_client import provide_chroma_client


class VectorDBFactory(object):

    @staticmethod
    def create_vectordb_client(vector_db_config=None, embedding_configuration=None) -> VectorDbClient:
        """Factory function to create and return a VectorDbClient based on configuration."""
        return provide_chroma_client()
