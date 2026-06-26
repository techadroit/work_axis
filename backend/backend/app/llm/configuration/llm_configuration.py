from abc import abstractmethod, ABC

from langchain_core.globals import set_debug, set_verbose

from backend.app.llm.configuration.model_config import ModelConfig
from backend.app.llm.inference_provider.inference_provider import InferenceProvider
from backend.app.llm.model_provider.model_provider import ModelProvider


class LlmConfiguration(ABC):

    def __init__(self, model_config: ModelConfig, model_provider: ModelProvider = None,
                 inference_provider: InferenceProvider = None):
        self.model_config = model_config
        self.model_provider = model_provider
        self.inference_provider = inference_provider
        # set_debug(True)
        # set_verbose(True)

    @abstractmethod
    def get_chat_llm(self):
        pass
