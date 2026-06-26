# from langchain.globals import set_debug, set_verbose

from backend.app.llm.configuration.embedding_configuration import EmbeddingConfiguration
from backend.app.llm.configuration.llm_configuration import LlmConfiguration
from backend.app.llm.ToolHandler import ToolHandler

# set_debug(True)
# set_verbose(True)

class LlmHandler:

    def __init__(self, llm_config: LlmConfiguration = None,
                 embedding_config: EmbeddingConfiguration = None, tool_handler=ToolHandler()):
        self.llm_config = llm_config
        self.embedding_config = embedding_config
        self.tool_handler = tool_handler

    def execute_prompt(self, prompt: str):
        # Logic to execute the prompt using the configured LLM and embeddings
        llm = self.llm_config.get_chat_llm().bind_tools(tools=self.tool_handler.get_tools())
        return llm.invoke(prompt)

## embedding configuration
## llm configuration
## tool configuration
## chain configuration
## prompt to be executed
## response observer
