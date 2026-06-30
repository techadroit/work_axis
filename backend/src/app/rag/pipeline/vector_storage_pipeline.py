from src.app.llm.configuration.embedding_configuration import EmbeddingConfiguration
from src.app.rag.pipeline.base_pipeline import BasePipeline
from src.app.utils.logger_util import log_debug
from src.app.vector_db.base.vector_db_client import VectorDbClient
from src.app.vector_db.base.vector_db_config import VectorDbConfig


class VectorStoragePipeline(BasePipeline):

    def __init__(self, client: VectorDbClient = None,
                 embedding_configuration: EmbeddingConfiguration = None,
                 vector_db_config: VectorDbConfig = None,
                 next_steps=None):
        self.client = client
        self.vector_db_config = vector_db_config
        self.collection_name = vector_db_config.get_collection_name()
        client.create_collection(collection_name=self.collection_name,
                                 vector_size=embedding_configuration.get_dimension(),
                                 distance=vector_db_config.get_distance())
        super().__init__(next_steps=next_steps)

    def process(self, data=None, **kwargs):
        log_debug("storing vectors")
        self.client.insert_vectors(collection_name=self.collection_name, data=data)
        self._call_next(data=data,**kwargs)
