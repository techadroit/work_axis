import asyncio

from langchain_core.messages import HumanMessage

from agents.doc_search.document_agent_graph import create_document_agent_graph
from agents.llm_handler.graph_llm_handler import get_graph_llm_handler
from agents.services.graph_llm_service import get_graph_llm_service
from rag.factory.rag_pipeline_factory import RagPipelineFactory
from src.app.utils.logger_util import log_response
from src.app.utils.model_util import get_default_model_config


async def run_document_agent_demo():
    pipeline_handler = RagPipelineFactory.create_rag_pipeline("../data/test_data/dev.pdf")
    await pipeline_handler.start(session_id="session_id",user_id="user_id")

    graph = create_document_agent_graph()
    graph_llm_handler = get_graph_llm_handler(llm_config=get_default_model_config(), graph=graph)
    graph_service = get_graph_llm_service(llm_handler=graph_llm_handler)
    response = ""
    async for stream in await graph_service.stream_ai(
        input_message={"messages": [
            # HumanMessage("What is the work experience of the person in the document?"),
            HumanMessage("What is this document about?")
        ]}):
        # response = response + stream.content
        log_response(stream)
    # log_response(response)

asyncio.run(run_document_agent_demo())
