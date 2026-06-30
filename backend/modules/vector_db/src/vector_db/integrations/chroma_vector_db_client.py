import os
import uuid
from typing import Any

import chromadb
from chromadb import Settings

from core.utils.file_util import get_vector_db_path
from core.utils.logger_util import log_debug
from vector_db.base.vector_db_client import VectorDbClient
from vector_db.base.vector_db_config import VectorDbConfig
from vector_db.models.vector_model import VectorModel, Payload


class ChromaVectorDbClient(VectorDbClient):
    """
    ChromaDB vector database client implementation.

    Supports both in-memory and persistent storage.
    """

    def __init__(self,
                 persist_directory: str = None,
                 vector_db_config: VectorDbConfig = None,
                 embedding_configuration: Any = None):
        """
        Initialize ChromaDB client.

        Args:
            persist_directory: Directory path for persistent storage. If None, uses in-memory mode.
            vector_db_config: Vector database configuration
            embedding_configuration: Embedding configuration
        """
        super().__init__(vector_db_config, embedding_configuration)

        if persist_directory is None:
            project_root = get_vector_db_path()
            persist_directory = os.path.join(project_root, "chromadb")

        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings(anonymized_telemetry=False))
        log_debug(f"ChromaDB client initialized with persist_directory: {persist_directory}")

    def get_client(self):
        """Returns the ChromaDB client instance."""
        return self.client

    def create_collection(self, collection_name: str, **kwargs):
        """
        Create a new collection in ChromaDB.

        Args:
            collection_name: Name of the collection
            **kwargs: Additional parameters (vector_size, distance_metric)
        """
        distance_metric = kwargs.get("distance", "cosine")

        # Map distance metrics to ChromaDB format
        metric_mapping = {
            "cosine": "cosine",
            "euclidean": "l2",
            "ip": "ip",  # inner product
        }

        chroma_metric = metric_mapping.get(distance_metric, "cosine")

        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            log_debug(f"Collection '{collection_name}' already exists")
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": chroma_metric}
            )
            log_debug(f"Created new collection '{collection_name}' with metric '{chroma_metric}'")

        return collection

    def delete_collection(self, collection_name: str):
        """
        Delete a collection from ChromaDB.

        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            log_debug(f"Deleted collection '{collection_name}'")
        except Exception as e:
            log_debug(f"Error deleting collection '{collection_name}': {e}")

    def insert_vectors(self, collection_name: str, data, **kwargs):
        """
        Insert vectors into a ChromaDB collection.

        Args:
            collection_name: Name of the collection
            data: Single VectorModel or list of VectorModel objects
            **kwargs: Additional parameters
        """
        # Handle both single VectorModel and list of VectorModel
        if not isinstance(data, list):
            data = [data]

        collection = self.client.get_collection(name=collection_name)

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for item in data:
            # Generate unique ID
            item_id = str(uuid.uuid4())
            ids.append(item_id)

            embeddings.append(item.embedding)
            documents.append(item.payload.document)
            metadata = item.payload.metadata.copy() if item.payload.metadata else {"empty": "empty"}
            metadatas.append(metadata)

            log_debug(
                f"Inserting vector - ID: {item_id}, Document length: {len(item.payload.document)}, Metadata: {metadata}")

        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        log_debug(f"Successfully inserted {len(data)} vectors into collection '{collection_name}'")

    def create_database(self, database_name: str, **kwargs):
        """
        ChromaDB doesn't have separate databases, collections are top-level.
        This is a no-op for compatibility.
        """
        log_debug(f"create_database called with '{database_name}' - ChromaDB uses collections directly")
        pass

    def query_vectors(self, collection_name: str, query, **kwargs):
        """
        Query vectors from ChromaDB collection.

        Args:
            collection_name: Name of the collection
            query: Query embedding vector (list of floats)
            **kwargs: Additional parameters (top_k, filter)
        """
        top_k = kwargs.get("top_k", 5)
        filter_query = kwargs.get("filter_query", None)
        where_filter = filter_query if filter_query else None

        collection = self.client.get_collection(name=collection_name)
        log_debug(f"Querying collection '{collection_name}' with top_k={top_k} and filter {where_filter}")

        # Perform query
        results = collection.query(
            query_embeddings=[query],
            n_results=top_k,
            where=where_filter
        )

        log_debug(f"Found {len(results['ids'][0])} results")

        # Convert results to VectorModel objects
        vectors = []

        if results['ids'] and len(results['ids']) > 0:
            for idx in range(len(results['ids'][0])):
                # Extract data from results
                doc_id = results['ids'][0][idx]
                document = results['documents'][0][idx] if results['documents'] else ""
                metadata = results['metadatas'][0][idx] if results['metadatas'] else {}
                distance = results['distances'][0][idx] if results['distances'] else 0.0
                embedding = results['embeddings'][0][idx] if results.get('embeddings') else None

                vector_model = VectorModel(
                    embedding=embedding,
                    payload=Payload(
                        document=document,
                        metadata=metadata
                    ),
                    distance=distance
                )

                log_debug(
                    f"Result {idx + 1}: distance={distance:.4f}, doc_length={len(document)}, preview={document[:100]}")
                vectors.append(vector_model)

        return vectors


# Singleton instance
_client = ChromaVectorDbClient(
    vector_db_config=VectorDbConfig(),
    embedding_configuration=None
)


def provide_chroma_client() -> VectorDbClient:
    """
    Provides a singleton instance of ChromaVectorDbClient.

    Returns:
        ChromaVectorDbClient instance
    """
    return _client
