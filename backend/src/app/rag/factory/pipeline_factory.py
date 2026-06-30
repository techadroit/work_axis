from src.app.rag.pipeline.chunking_pipeline import ChunkingPipeline
from src.app.rag.pipeline.embedding_pipeline import EmbeddingPipeline
from src.app.rag.pipeline.loader_pipeline import LoadFilePipeline
from src.app.rag.pipeline.vector_storage_pipeline import VectorStoragePipeline


class PipelineFactory:

    @staticmethod
    def create_loader_pipeline(file_path: str, **kwargs):
        """Create a loader pipeline for loading documents."""
        return LoadFilePipeline(file_path=file_path, **kwargs)

    @staticmethod
    def create_chunking_pipeline(chunk_size: int = 500, chunk_overlap: int = 50, **kwargs):
        """Create a chunking pipeline for splitting documents."""
        return ChunkingPipeline(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)

    @staticmethod
    def create_embedding_pipeline(**kwargs):
        """Create an embedding pipeline for vectorizing text chunks."""
        return EmbeddingPipeline(**kwargs)

    @staticmethod
    def create_vector_storage_pipeline(client, embedding_configuration=None, vector_db_config=None, **kwargs):
        """Create a vector storage pipeline for storing embeddings in Qdrant."""
        return VectorStoragePipeline(
            client=client,
            embedding_configuration=embedding_configuration,
            vector_db_config=vector_db_config,
            **kwargs
        )

