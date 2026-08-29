from abc import ABC, abstractmethod
from typing import Any

from vector_db.base.vector_db_config import VectorDbConfig


class VectorDbClient(ABC):

    def __init__(self, vector_db_config: VectorDbConfig = None,
                 embedding_configuration: Any = None):
        self.vector_db_config = vector_db_config
        self.embedding_configuration = embedding_configuration

    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def create_database(self, database_name: str, **kwargs):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, **kwargs):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def insert_vectors(self, collection_name: str, data: Any, **kwargs):
        pass

    @abstractmethod
    def query_vectors(self, collection_name: str, query: Any, **kwargs):
        pass

    @abstractmethod
    def delete_by_filter(self, collection_name: str, filter_query: dict):
        pass
