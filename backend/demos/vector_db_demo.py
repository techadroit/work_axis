from qdrant_client import QdrantClient, models

from backend.app.rag.pipeline.chunking_pipeline import ChunkingPipeline
from backend.app.rag.pipeline.embedding_pipeline import EmbeddingPipeline
from backend.app.rag.pipeline.loader_pipeline import LoadFilePipeline
from backend.app.rag.pipeline.log_pipeline import LogPipeline
from backend.app.rag.pipeline.vector_storage_pipeline import VectorStoragePipeline

client = QdrantClient(":memory:")  # Qdrant is running from RAM.

docs = [
    "Qdrant has a LangChain integration for chatbots.",
    "Qdrant has a LlamaIndex integration for agents.",
]
metadata = [
    {"source": "langchain-docs"},
    {"source": "llamaindex-docs"},
]
ids = [42, 2]

log_pipeline = LogPipeline()
# vector_storage_pipeline = VectorStoragePipeline(next_steps=log_pipeline)
# embedding_pipeline = EmbeddingPipeline(next_steps=vector_storage_pipeline)
# splitter = ChunkingPipeline(next_steps=embedding_pipeline)
loader = LoadFilePipeline(file_path="../data/files/ai_claim.pdf", next_steps=log_pipeline)
# loader.process()

# model_name = "BAAI/bge-small-en"
# client.create_collection(
#     collection_name="test_collection",
#     vectors_config=models.VectorParams(
#         size=client.get_embedding_size(model_name),
#         distance=models.Distance.EUCLID
#     ),  # size and distance are model dependent
# )
#
# metadata_with_docs = [
#     {"document": doc, "source": meta["source"]} for doc, meta in zip(docs, metadata)
# ]
# client.upload_collection(
#     collection_name="test_collection",
#     vectors=[models.Document(text=doc, model=model_name) for doc in docs],
#     payload=metadata_with_docs,
#     ids=ids,
# )
#
# search_result = client.query_points(
#     collection_name="test_collection",
#     query=models.Document(
#         text="Which integration is best for agents?",
#         model=model_name
#     )
# ).points
# print(search_result)