from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.app.utils.embedding_util import create_default_embedding_model
from core.utils.logger_util import log_debug, log_error, log_info
from vector_db.base.vector_db_config import VectorDbConfig
from vector_db.models.vector_model import VectorModel
from vector_db.vectordb_factory import VectorDBFactory


class DocumentSearchInput(BaseModel):
    """Input schema for document search tool"""
    query: str = Field(description="Search query to find relevant document sections")
    top_k: int = Field(default=5, description="Number of top results to return (default: 5)")
    session_id: str = Field(description="Session id of session to use")


@tool("search_documents", description="Use this tool to find documents from the vector store",
      args_schema=DocumentSearchInput)
def search_documents_tool(query: str, session_id: str, top_k: int = 5, ) -> str:
    """
    Search vector database for relevant document chunks using QdrantVectorDbClient.

    Args:
        query: The search query to find relevant documents
        top_k: Number of top results to return

    Returns:
        Formatted string with search results or error message
        :param session_id:
    """
    try:
        log_debug(f"Searching documents with query: {query}")

        vector_db_config = VectorDbConfig()
        vector_db = VectorDBFactory.create_vectordb_client(vector_db_config=vector_db_config)

        # Get embedding model to embed the query
        embedding_model = create_default_embedding_model()
        query_embedding = embedding_model.embed_query(query)
        filter_query = {"session_id": {
            "$eq": session_id
        }} if session_id is not None else None

        # Search vector database
        results: list[VectorModel] = vector_db.query_vectors(
            collection_name=vector_db_config.get_collection_name(),
            query=query_embedding,
            filter_query=filter_query,
        )

        if not results:
            # log_info("No relevant documents found")
            return "No relevant documents found matching your search query."

        # Format results
        formatted_results = []
        for result in results:
            payload = result.payload
            content = payload.document
            log_info(f"Found document: {content}")
            formatted_results.append(content)

        response = formatted_results.__str__()
        return response

    except Exception as e:
        error_msg = f"Error searching documents: {str(e)}"
        log_error(error_msg)
        return error_msg
