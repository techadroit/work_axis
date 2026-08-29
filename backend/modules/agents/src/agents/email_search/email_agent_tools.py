from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.app.utils.embedding_util import get_cached_default_embedding_model
from core.utils.logger_util import log_debug, log_error, log_info
from vector_db.base.vector_db_config import VectorDbConfig
from vector_db.models.vector_model import VectorModel
from vector_db.vectordb_factory import VectorDBFactory


class EmailSearchInput(BaseModel):
    """Input schema for email search tool"""
    query: str = Field(description="Search query to find relevant emails")
    top_k: int = Field(default=10, description="Number of top results to return (default: 10)")
    user_id: str = Field(description="ID of the user whose emails should be searched")


@tool("search_emails", description="Use this tool to search the user's ingested emails (Gmail or imported files)",
      args_schema=EmailSearchInput)
def search_emails_tool(query: str, user_id: str, top_k: int = 10) -> str:
    """
    Search vector database for relevant email chunks, scoped to the given user.

    Args:
        query: The search query to find relevant emails
        user_id: ID of the user whose emails should be searched
        top_k: Number of top results to return

    Returns:
        Formatted string with search results (including sender/subject/date) or error message
    """
    try:
        # The LLM sometimes passes an invalid top_k (0, negative, or an
        # unreasonably large number) - clamp defensively rather than letting
        # a bad value reach Chroma (which rejects n_results <= 0 outright).
        if not isinstance(top_k, int) or top_k <= 0:
            top_k = 10
        top_k = min(top_k, 25)

        log_debug(f"Searching emails with query: {query} for user {user_id} (top_k={top_k})")

        vector_db_config = VectorDbConfig()
        vector_db = VectorDBFactory.create_vectordb_client(vector_db_config=vector_db_config)

        embedding_model = get_cached_default_embedding_model()
        query_embedding = embedding_model.embed_query(query)
        filter_query = {"$and": [
            {"source": {"$eq": "email"}},
            {"user_id": {"$eq": user_id}},
        ]}

        results: list[VectorModel] = vector_db.query_vectors(
            collection_name=vector_db_config.get_collection_name(),
            query=query_embedding,
            top_k=top_k,
            filter_query=filter_query,
        )

        if not results:
            return "No relevant emails found matching your search query."

        formatted_results = []
        for result in results:
            metadata = result.payload.metadata or {}
            formatted_results.append(
                f"From: {metadata.get('from', 'unknown')}\n"
                f"Subject: {metadata.get('subject', '(no subject)')}\n"
                f"Date: {metadata.get('date', 'unknown')}\n"
                f"Content: {result.payload.document}"
            )
            log_info(f"Found email chunk: subject={metadata.get('subject')}")

        return "\n\n---\n\n".join(formatted_results)

    except Exception as e:
        error_msg = f"Error searching emails: {str(e)}"
        log_error(error_msg)
        return error_msg
