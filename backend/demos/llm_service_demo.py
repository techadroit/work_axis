import asyncio

from langchain.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from demos.stream_callback_handler import StreamCallbackHandler
from llm.LLMService import LLMService
from llm_module.llm_handler.llm_handler import LlmHandler
from llm_module.ToolHandler import ToolHandler
from agents.web_search.web_search_agents import crete_web_search_agent
from agents.app_graph import AppState
from src.app.utils.model_util import create_model_config, get_default_model_config
from langgraph.graph import START

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


@tool("get_current_weather",
      description="Use this to know the current weather of a location or city")
def get_weather(location: str):
    """Get the current weather in a given location"""
    return f"Now the weather in {location} is sunny"


TEMPERATURE = 0.1
TOP_P = 0.5
model_config = create_model_config(temperature=TEMPERATURE, top_p=TOP_P, max_retries=2)

"""
Create tools to be called
"""
tool_handler = ToolHandler()
tool_handler.append_tools([get_weather])

# llm_handler = LlmHandler(llm_config=create_azure_config(model_config), tool_handler=tool_handler)
llm_handler = LlmHandler(llm_config=get_default_model_config())
# llm_handler = LlmHandler(llm_config=create_together_config(model_config=model_config))
# llm_handler = LlmHandler(llm_config=create_openai_config(model_config=model_config),tool_handler=tool_handler)
# llm_handler = LlmHandler(llm_config=create_claude_config(model_config=model_config),tool_handler=tool_handler)
# llm_handler = LlmHandler(llm_config=create_gemini_config(model_config=model_config),tool_handler=tool_handler)
# llm_handler = LlmHandler(llm_config=create_aws_bedrock_config(model_config),tool_handler=tool_handler)

llm_service = LLMService(llm_handler=llm_handler)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])


# ai_msg = llm_service.execute(
#     prompt.invoke({"input": "What is the weather of france?"})
# )
#
# ai_msg1 = llm_service.execute(
#     prompt.invoke({"input": "What is the capital of france?"})
# )
#
# log_response(ai_msg)
# log_response(ai_msg1)

async def response_node(app_state: AppState, config):
    response = await llm_handler.agraph_stream("Generate a poem about AI.", config=config)
    return {"messages": response.content}


async def run_graph_demo():
    from agents.app_graph import AppGraph
    from langgraph.graph import StateGraph

    graph = StateGraph(AppState)
    graph.add_node("response_node", response_node)
    graph.add_edge(START, "response_node")

    app_graph = AppGraph(graph=graph)
    # Fix: Use HumanMessage() constructor, not brackets
    messages = [HumanMessage(content="Generate a poem about AI.")]

    # Fix: Use async for, not for...await
    await llm_handler.astream_graph(graph=app_graph, messages=messages)


async def run_demo():
    await llm_service.astream(prompt=prompt.invoke({"input": "Generate a poem about AI."}).to_string(),
                              stream_handler=StreamCallbackHandler())


# asyncio.run(run_demo())
# asyncio.run(run_graph_demo())
# run_demo()
# chat_mode = ChatMode(mode=AgentMode.ON)
# asyncio.run(llm_service.handle_messages(
#     messages=create_chat_message(messages="What is the weather of france?",chat_mode=chat_mode),
#     stream_handler = StreamCallbackHandler()
# ))


async def run_graph():
    graph = crete_web_search_agent()
    llm_service = LLMService(llm_handler=llm_handler)
    await llm_service.astream_graph(graph, [HumanMessage("What is the recent investment related to AI?")],
                                    StreamCallbackHandler())


asyncio.run(run_graph())