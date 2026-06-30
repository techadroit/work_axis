# ...existing code...
import asyncio

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from src.app.llm.agents.agentic_mode.agent_node import agent_mode, AGENT_ROUTER_PROMPT
from src.app.llm.agents.persistence.database_check_pointer import provide_checkpointer
from src.app.llm.llm_handler.graph_llm_handler import get_graph_llm_handler
from src.app.llm.services.graph_llm_service import get_graph_llm_service
from src.app.utils.logger_util import log_response, log_debug
from src.app.utils.message_util import extract_ai_message
from src.app.utils.prompt_util import format_prompt


async def run_graph(message: str):
    session_config: RunnableConfig = {"configurable": {"thread_id": "session_id234567"}}
    async with provide_checkpointer() as checkpointer:
        graph = agent_mode(checkpointer=checkpointer)
        graph_llm_handler = get_graph_llm_handler(graph=graph)
        graph_service = get_graph_llm_service(llm_handler=graph_llm_handler)
        full_response = ""
        async for chunk in await graph_service.stream_ai(
                input_message={"messages": [HumanMessage(message)]},
                session_config=session_config):
            msg = extract_ai_message(chunk)
            if msg is not None:
                full_response += msg.content
            log_response(f"chunk: {chunk}")
        log_response(full_response)
        log_response("graph completed")


async def main():
    await run_graph("My name is Dev")
    await asyncio.sleep(1)
    await run_graph("What is my name?")


# asyncio.run(main())

# asyncio.run(run_graph("Hello how are you"))
# asyncio.run(run_graph("My name is Dev"))
# asyncio.run(run_graph("What is my name?"))
# asyncio.run(run_graph("new stories about linkedin"))
# asyncio.run(run_graph("can we use linkedin to find jobs?"))
# asyncio.run(run_graph("ok"))


# wrapper = DuckDuckGoSearchAPIWrapper(region="in", max_results=5)
# search = DuckDuckGoSearchResults(output_format="list",api_wrapper=wrapper)
# response = search.invoke("Who won world cup 2025 womens?")
# log_response(response)

# wrapper = DuckDuckGoSearchAPIWrapper(region="in", time="d", max_results=5)
# search = DuckDuckGoSearchResults(api_wrapper=wrapper)
# response = search.invoke("Who won world cup 2025 womens?")
# log_response(response)

# retrieval_node(state={"search_query": "Who won women's cricket world"})


# async def summarize_demo_node(state:AppState):
#     log_debug("Starting summarize_demo_node")
#     log_debug(state)
#     # summarization_result = await summarization_node(state, config={})
#     log_debug("Summarization result:")
#     # log_debug(summarization_result)
#     return state
#
#
# async def main():
#     graph = StateGraph(AppState)
#     graph.add_node("summarization_node", summarization_node)
#     graph.add_node("summarize_demo_node", summarize_demo_node)
#     graph.add_edge(START, "summarization_node")
#     graph.add_edge("summarization_node", "summarize_demo_node")
#     graph.add_edge("summarize_demo_node", END)
#
#     app_graph = AppGraph(graph)
#     service = get_graph_service(app_graph)
#     result = await service.ask_ai({"messages": ["Who is Virat Kohli?"]})
#     log_debug("Final state after summarization:")
#     log_debug(result)
#
#
# # asyncio.run(main())

def check_prompt():
    prompt = AGENT_ROUTER_PROMPT
    # prompt = PromptTemplate.from_template(template=prompt).format(conversation_history="Test conversation history")
    prompt = format_prompt(prompt, conversation_history="Test conversation history")
    log_debug(prompt)

# Create test state
# test_state: WebSearchState = {
#     "messages": [
#         AIMessage(
#             content="Here is a concise summary of the conversation:\n\nYou introduced yourself as Dev, but later corrected that your name is actually Jishan. We discussed Virat Kohli's ODI stats and you asked about Sachin Tendulkar's cricket career. You then inquired about Hardik Pandya and requested his career statistics, which I provided.",
#             additional_kwargs={},
#             response_metadata={
#                 'model': 'llama3.1:8b',
#                 'created_at': '2026-01-08T05:11:38.119341Z',
#                 'done': True,
#                 'done_reason': 'stop',
#                 'total_duration': 14684455041,
#                 'load_duration': 3522681625,
#                 'prompt_eval_count': 1781,
#                 'prompt_eval_duration': 2408126834,
#                 'eval_count': 71,
#                 'eval_duration': 3102835500,
#                 'model_name': 'llama3.1:8b',
#                 'model_provider': 'ollama'
#             },
#             id='lc_run--f34703ea-c08f-42d4-9aa3-9edc37d22cc9-0',
#             usage_metadata={'input_tokens': 1781, 'output_tokens': 71, 'total_tokens': 1852}
#         ),
#         HumanMessage(content='?', id='737be365-8d65-4cc7-abaf-a1e46a77c518'),
#         AIMessage(
#             content="It seems we haven't started the conversation yet! Let's begin fresh.\n\nHi there! How are you doing today? Is there anything on your mind that you'd like to talk about or ask me?",
#             id='b78a8387-80a2-440d-9b87-bfa96646b0d0'
#         ),
#         HumanMessage(content='can you list hardik pandya achievements', id='44b172cc-7db9-4994-bb5d-dd9fc9157e28'),
#         AIMessage(
#             content="Hardik Pandya is a talented cricketer from India. I think I mentioned his stats earlier in our conversation, but let me refresh your memory. Hardik Pandya has achieved many milestones in his career.\n\nHere are some of his notable achievements:\n\n* He made his ODI debut against Australia in 2016 and has since become a regular member of the Indian team.\n* In January 2020, he took 4 wickets for just 12 runs in an over against Australia, becoming the first Indian bowler to achieve this feat in ODIs.\n* He is also known for his impressive batting skills, particularly in T20 cricket. He has scored many crucial runs for India and has been a key player in their success.\n\nPlease let me know if you'd like more information on Hardik Pandya's achievements!",
#             id='9a3f2aa8-ea26-4d95-a25d-ae66faac0cb1'
#         ),
#         HumanMessage(content='more information', id='0c5d780d-ed3a-4220-8200-6fe8382188aa'),
#         AIMessage(
#             content='',
#             tool_calls=[{
#                 'name': 'search_documents',
#                 'args': {'query': 'more information about Hardik Pandya cricket career', 'top_k': 10},
#                 'id': '8f3ce5d8-bf2f-4b68-b623-fe3e916abc91',
#                 'type': 'tool_call'
#             }],
#             id='lc_run--be0a5a93-5643-441a-981d-4a6b1f3737e7-0',
#             usage_metadata={'input_tokens': 795, 'output_tokens': 32, 'total_tokens': 827}
#         ),
#         ToolMessage(
#             content='Error searching documents: Collection test_collection not found',
#             name='search_documents',
#             id='f6bb7218-ae21-4ca2-b9d2-2c26426e3703',
#             tool_call_id='8f3ce5d8-bf2f-4b68-b623-fe3e916abc91'
#         ),
#         AIMessage(
#             content='It seems like I was unable to find the necessary documents. Let me try again.\n\n{"name": "search_documents", "parameters": {"query":"Hardik Pandya cricket career statistics and achievements","top_k":10}}',
#             id='lc_run--c4c60fec-10f8-44e1-a801-b45be6f08ecd-0'
#         ),
#         AIMessage(content='', id='8cc839ed-7bae-4cc0-ac77-c72dea8e10a6'),
#         HumanMessage(content='can you search the web?', id='c66b75ce-6c57-416a-ae61-f9432bb9e831'),
#         HumanMessage(content='can you search the web again', id='87431146-1d80-4cfe-99ca-5539e8fb1f38'),
#         HumanMessage(content='?', id='ec1d94b2-4306-4152-b90f-b624bb1125bb'),
#         HumanMessage(content='?', id='1990284e-68b0-409a-b41e-27fec99f5188'),
#         HumanMessage(content='?', id='3cd32ca6-df3c-402d-86e0-ccec4f160ff1'),
#         HumanMessage(content='?', id='11cbb147-6179-42af-a804-a7b736922c97'),
#         HumanMessage(content='?', id='9418ef86-32cc-462a-9954-55b89e0a132e'),
#         HumanMessage(content='Search internet for sachin tendulkar statistics',
#                      id='f9fbbcdc-bdca-4991-a592-56ec8dce2183')
#     ],
#     "route": "web_search"
# }
#
# async def run_test_web():
#     for i in range(10):
#         try:
#             response = await web_search_start_node(test_state)
#             log_response(response)
#         except Exception as e:
#             log_response(f"Error during agent routing: {e}")
#
# async def run_test():
#     for i in range(1):
#         try:
#             graph = agent_mode()
#             async for response in await get_graph_service(graph).stream_ai(
#                     input_message={"messages": ["My name is Dev?"]}):
#                 log_response(response)
#         except Exception as e:
#             log_response(f"Error during agent routing: {e}")


# asyncio.run(run_test())
