import asyncio

from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient

from backend.app.llm.ToolHandler import ToolHandler
from backend.app.llm.llm_handler.chat_llm_handler import ChatLLMHandler
from backend.app.llm.services.agent_service import AgentService
from backend.app.utils.logger_util import log_response
from backend.app.utils.model_util import get_default_model_config

system_prompt = """
Role : You are a helpful AI assistant that provides brief, concise answers.

TOOL USAGE RULES:
1. ONLY use tools when the question CANNOT be answered from your knowledge
2. For common facts and general knowledge questions, answer directly WITHOUT mentioning tools
3. Never suggest a tool that doesn't directly answer the user's question

RESPONSE FORMAT:
- Keep answers direct
- No explanations about your thinking process

"""

mcp_client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "streamable_http",  # HTTP-based remote server
            # Ensure you start your weather server on port 8000
            "url": "http://localhost:8000/mcp",
        }
    }
)


async def run_demo():
    tool_handler = ToolHandler()
    tools = await mcp_client.get_tools()
    tool_handler.append_tools(tools)
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}")
    ])
    prompt = prompt.invoke({"input": "What is the weather of france?"})
    chat_llm_handler = ChatLLMHandler(llm_config=get_default_model_config(), tool_handler=tool_handler)
    agent_service = AgentService(llm_handler=chat_llm_handler)
    agent = agent_service.create_agent(system_prompt=system_prompt, tools=tool_handler)
    response = await agent.ainvoke(input=prompt)
    log_response(response)


asyncio.run(run_demo())
