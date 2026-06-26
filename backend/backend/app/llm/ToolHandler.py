from typing import Sequence, Union, Callable, Any

from langchain_core.tools import BaseTool


class ToolHandler:
    tools: Sequence[Union[dict[str, Any], type, Callable, BaseTool]] = []

    def __init__(self):
        self.tools = []

    def append_tools(self, new_tools: Sequence[Union[dict[str, Any], type, Callable, BaseTool]]):
        self.tools = new_tools

    def get_tools(self):
        return self.tools

    @classmethod
    def create(cls, tools = None):
        instance = cls()
        if tools:
            instance.append_tools(tools)
        return instance