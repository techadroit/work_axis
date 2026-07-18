from rag.pipeline.chunking_pipeline import ChunkingPipeline
from rag.pipeline.embedding_pipeline import EmbeddingPipeline
from rag.pipeline.loader_pipeline import LoadFilePipeline
from rag.pipeline.log_pipeline import LogPipeline
from rag.pipeline.pipeline_handler import PipelineHandler
from rag.pipeline.vector_storage_pipeline import VectorStoragePipeline
from src.app.utils.embedding_util import create_sentence_transformer_embedding_model
from vector_db.base.vector_db_config import VectorDbConfig
from vector_db.vectordb_factory import VectorDBFactory


class RagPipelineFactory:

    @staticmethod
    def create_rag_pipeline(file_path: str,**kwargs) -> PipelineHandler:
        """
        Create a complete RAG pipeline with default configuration.

        Chains together:
        1. LoadFilePipeline - Loads document from file
        2. ChunkingPipeline - Splits document into chunks
        3. EmbeddingPipeline - Vectorizes text chunks
        4. VectorStoragePipeline - Stores embeddings in Qdrant
        5. LogPipeline - Logs the results

        Args:
            file_path: Path to the document file to process
            chunk_size: Size of text chunks (default: 500)
            chunk_overlap: Overlap between chunks (default: 50)

        Returns:
            LoadFilePipeline: The entry point of the pipeline chain
        """
        log_pipeline = LogPipeline()
        vector_db_config = VectorDbConfig()
        # Use SentenceTransformer with 384 dimensions
        embedding_configuration = create_sentence_transformer_embedding_model()
        vector_storage_pipeline = VectorStoragePipeline(client=VectorDBFactory.create_vectordb_client(),
                                                        vector_db_config=vector_db_config,
                                                        embedding_configuration=embedding_configuration,
                                                        next_steps=log_pipeline)
        embedding_pipeline = EmbeddingPipeline(next_steps=vector_storage_pipeline)
        splitter = ChunkingPipeline(next_steps=embedding_pipeline)
        loader = LoadFilePipeline(file_path=file_path, next_steps=splitter)
        return PipelineHandler(pipelines=[loader])
