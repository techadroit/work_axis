from backend.app.vector_db.base.VectorDistance import VectorDistance


class VectorDbConfig:

    def get_collection_name(self) -> str:
        return "test_collection"

    def get_distance(self) -> VectorDistance:
        return VectorDistance.COSINE

    def get_vectordb_provider(self) -> str:
        return "chromadb"
