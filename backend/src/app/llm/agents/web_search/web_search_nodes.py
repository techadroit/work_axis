from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate

from core.errors import RetryableError
from src.app.llm.agents.AgentConstants import APP_MESSAGES
from web_search import tool_extract_webpage_content, tool_search_web

from src.app.llm.llm_handler.chat_llm_handler import ChatLLMHandler
from src.app.llm.services.chat_llm_service import get_chat_llm_service
from src.app.llm.services.llm_service import get_llm_service
from src.app.llm.services.llm_service_factory import LLMServiceFactory
from src.app.prompts.markdown_response_format import mark_down_response_format
from src.app.server.base.app_graph import WebSearchState
from core.utils.json_util import parse_get_json
from src.app.utils.logger_util import log_response, log_debug, log_node
from src.app.utils.model_util import get_default_model_config


# chat_llm_handler = ChatLLMHandler(llm_config=get_default_model_config())
# llm_handler = get_llm_handler(llm_config=get_default_model_config())
# llm_service = get_llm_service(llm_handler=llm_handler)
# chat_llm_service = get_chat_llm_service(llm_handler=chat_llm_handler)


async def web_search_start_node(state: WebSearchState):
    log_node("Web Search Start Node: ")
    _web_search_node_system_prompt = """
You are an expert query router for a chat llm application. 
Your only goal is to analyze the conversation history and decide which route to take based on the available routes.
You must choose only one route.
You will be provided with chat history between a user and an AI assistant.

### Available Routes:
1. **web_search_conversation_node** - For greetings, farewells, or questions answerable from conversation history
2. **planning_node** - For queries requiring current/external information from the internet

## Your task:
- Analyze Conversation History and decide which route to select.
- You will be provided with multiple questions from the user but you should select only one route.
- Based on the user intent, choose one of the available routes.
- Never select multiple routes.
- If you are uncertain about which route to choose, default to "web_search_conversation_node".
    
Guidelines:
- Always check the conversation history to see if the answer is already available.
- Only route to the `planning_node` if an internet search is required.
- Do not fabricate information or make assumptions.

Respond ONLY with a JSON object in the following format:
{"route": "web_search_conversation_node"}  // for simple or history-based responses
{"route": "planning_node"}                 // for queries needing internet search and planning

### Response Format (JSON only, no explanations):
{"route": "node_name"}

### Important Rules:
- Multiple routes are not allowed.
- Output only one route based on the user intent based on the conversation history
- Output ONLY valid JSON in the exact format shown
- Do not include reasoning, explanations, or multiple responses
- If uncertain, default to "web_search_conversation_node"
"""

    messages = [SystemMessage(content=_web_search_node_system_prompt)] + state[APP_MESSAGES]
    chat_llm_handler = ChatLLMHandler(llm_config=get_default_model_config())
    chat_llm_service = get_chat_llm_service(chat_llm_handler)
    response = await chat_llm_service.ask_ai(messages)
    route = ""
    try:
        log_response(response.content)
        route = parse_get_json("route", response.content)
    except Exception as e:
        log_debug(f"Error parsing route: {response}")
        raise RetryableError(f"Failed to parse route from LLM response. {route}")
    state["route"] = route
    return state


async def web_search_conversation_node(state: WebSearchState, config, writer):
    log_node("web_search_conversation_node ")
    # For use in web_search_conversation_node
    _web_search_conversation_node_system_prompt = """
    You are a friendly and helpful assistant.
    Your task is to respond conversationally to the user's message. 
    If the user asks about something discussed earlier, look up the chat history to provide a relevant answer. 
    If the answer can be found in the chat history, use that information.
     If not, reply naturally as a helpful assistant would.
    Do not use any external or internet information. 
    Only use the chat history and your general conversational abilities.
    Always keep your responses clear, concise, and polite.
    """

    input_messages = [SystemMessage(content=_web_search_conversation_node_system_prompt)] + state.get(APP_MESSAGES, [])
    
    full_response = ""
    llm_service = get_llm_service()
    async for stream in llm_service.stream_ai(input_message=input_messages, config=config):
        full_response += stream.content
        writer({APP_MESSAGES: stream.content})
    return {APP_MESSAGES: AIMessage(full_response)}


from pydantic import BaseModel, Field
from typing import List


class WebSearchQueryResponse(BaseModel):
    search_query: List[str] = Field(
        description="List of search queries to be executed, maximum 3 queries",
        max_length=3,
        min_length=1
    )


async def planning_node(state: WebSearchState):
    log_node("Planning Node: ")
    log_node(state)

    system_prompt = f"""
    You are a web search agent that helps users find information from the web.
    Your task is to only create search queries based on the user's questions and output should follow the response format.
    You will be provided with the chat history between the user and the assistant.
    
    You should consider the following steps:
    1. Understand the user's query and identify the key information needed.
    2. Formulate a search query that will be used to search the web.

    Guidelines:
    - The search query you generate must match the context, details, and intent of the user's question.
    - Do NOT substitute years, names, places, or other specifics with similar or popular alternatives.
    - If the user asks about a future event or something not yet occurred, use the details as stated.
    - You can create max 3 search queries.

    Here are some examples:
    Example 1:
    User: Who won the 2025 Women's Cricket World Cup?
    Output: {{"search_query": ["Who won the 2025 Women's Cricket World Cup?"]}}

    Example 2:
    User: What's the weather like in Paris today?
    Output: {{"search_query": ["Weather in Paris today"]}}

    Example 3:
    User: Tell me about the latest iPhone features.
    Output: {{"search_query": ["Latest iPhone features"]}}

    Example 4:
    User: How tall is Mount Everest?
    Output: {{"search_query": ["Mount Everest height"]}}

    Example 5:
    User: What movies did Leonardo DiCaprio star in?
    Output: {{"search_query": ["Leonardo DiCaprio movies"]}}

    Example 6:
    User: Who is the current president of Brazil?
    Output: {{"search_query": ["Current president of Brazil, ""President of Brazil"]}}

    Example 7:
    User: What is the capital of Mongolia?
    Output: {{"search_query": ["Capital of Mongolia","Mongolia Capital"]}}

    Example 8:
    User: How do I bake a chocolate cake?
    Output: {{"search_query": ["Chocolate cake recipe","Cake recipes"]}}

    """
    log_response(system_prompt)
    messages = [SystemMessage(content=system_prompt)] + state[APP_MESSAGES]

    try:
        chat_llm_service = LLMServiceFactory.get_new_chat_llm_service()
        response = await chat_llm_service.ask_ai(messages, output_model=WebSearchQueryResponse)
        state["search_query"] = response.search_query
    except Exception as e:
        log_debug(f"Error parsing search_query: {e}")
        raise RetryableError("Failed to parse search_query from LLM response.")
    log_debug(f"Formulated search query: {state.get('search_query', '')}")
    return {APP_MESSAGES: state[APP_MESSAGES], "search_query": state.get("search_query", "")}


def retrieval_node(state: WebSearchState):
    # Step 1: Search the web

    knowledge_base = []

    log_debug(f"Retrieval node: {state.get('search_query', '')}")

    for query in state["search_query"]:
        response = tool_search_web(query)
        urls = [item['link'] for item in response]

        for url in urls:
            # Step 2: Extract content from each URL
            content_result = tool_extract_webpage_content(url)
            # Assume content_result contains 'title', 'content', and optionally 'source'
            knowledge_base.append({
                "url": url,
                "title": content_result.get("title", ""),
                "content": content_result.get("content", ""),
                "source": content_result.get("source", url)
            })

    # Step 3: Add extracted knowledge to state for the next node
    state["knowledge_base"] = knowledge_base

    # Optionally, update messages for traceability
    state[APP_MESSAGES].append({
        "role": "system",
        "content": f"Knowledge base created from URLs: {[kb['url'] for kb in knowledge_base]}"
    })

    return {
        APP_MESSAGES: state[APP_MESSAGES],
        "knowledge_base": knowledge_base
    }


async def generator_node(state: WebSearchState, config, writer):
    system_prompt = f"""
    You are a generator agent that creates a coherent and informative response from the given chat history and extracted web content.
    You will be given a chat history of conversation between a user and an assistant, as well as a knowledge base containing content extracted from relevant web pages.

    Your task is to generate a final response that addresses the user's query using the information provided in the chat history and the knowledge base.
    Make sure to summarize the key points and provide a clear answer.

    Do not include any tool calls or results in your final response.
    Do not include any references to the tools used.
    Do not include any explanations about your thinking process.

    <CHAT_HISTORY>
    {{chat_history}}
    </CHAT_HISTORY>
    <KNOWLEDGE_BASE>
    {{knowledge_base}}
    </KNOWLEDGE_BASE>
    
    {mark_down_response_format}
    """

    # Format the knowledge base for the prompt
    knowledge_base_str = ""
    for kb in state.get("knowledge_base", []):
        knowledge_base_str += f"- Title: {kb.get('title', '')}\n  URL: {kb.get('url', '')}\n  Content: {kb.get('content', '')}\n\n"

    prompt = PromptTemplate.from_template(system_prompt).invoke({
        "chat_history": state[APP_MESSAGES],
        "knowledge_base": knowledge_base_str
    })
    full_response = ""
    llm_service = LLMServiceFactory.get_new_llm_service()
    async for stream in llm_service.stream_ai(input_message=prompt.to_string(), config=config):
        full_response += stream.content
        writer({APP_MESSAGES: stream.content})
    return {APP_MESSAGES: AIMessage(full_response)}


def evaluation_agent(state: WebSearchState):
    return {APP_MESSAGES: state[APP_MESSAGES]}
