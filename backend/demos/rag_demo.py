from src.app.rag.factory.rag_pipeline_factory import RagPipelineFactory

# log_pipeline = LogPipeline()
# vector_db_config = VectorDbConfig()
# embedding_configuration = get_embedding_config()
# vector_storage_pipeline = VectorStoragePipeline(client=provide_db_client(),
#                                                 vector_db_config=vector_db_config,
#                                                 embedding_configuration=embedding_configuration,
#                                                 next_steps=log_pipeline)
# embedding_pipeline = EmbeddingPipeline(next_steps=vector_storage_pipeline)
# splitter = ChunkingPipeline(next_steps=embedding_pipeline)
# loader = LoadFilePipeline(file_path="../data/files/demo_doc_2.pdf", next_steps=splitter)
# loader.process()
#
# client = provide_db_client()
# embedding_model = create_embedding_model()
# data = client.query_vectors(collection_name=vector_db_config.get_collection_name(),
#                             query=embedding_model.embed_query(
#                                 "list his work experience"), )
# log_info(f"data: {data}")

# pipeline_handler = RagPipelineFactory.create_rag_pipeline("../data/files/demo_doc_2.pdf")
# pipeline_handler.start()
