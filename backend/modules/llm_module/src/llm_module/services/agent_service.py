from langchain.agents import create_agent
from langgraph.prebuilt import create_react_agent

from llm_module.ToolHandler import ToolHandler
from llm_module.llm_handler.chat_llm_handler import ChatLLMHandler
from llm_module.llm_messages.base_llm_messages import TOOL_TYPE


class AgentService:
    def __init__(self, llm_handler: ChatLLMHandler):
        self.llm_handler = llm_handler

    def create_agent(self, system_prompt: str, tools: ToolHandler = None):
        agent = create_agent(
            model=self.llm_handler._get_llm(),
            tools=tools.get_tools(),
            system_prompt=system_prompt,
        )
        return agent

    def create_reactive_agent(self, system_prompt: str, tools: [TOOL_TYPE] = None):
        agent = create_react_agent(
            model=self.llm_handler._get_llm(),
            tools=tools,
            system_prompt=system_prompt
        )
        return agent

