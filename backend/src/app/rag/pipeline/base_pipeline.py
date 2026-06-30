from abc import ABC, abstractmethod

from src.app.utils.logger_util import log_debug


class BasePipeline(ABC):

    def __init__(self, next_steps=None, strategy=None):
        super().__init__()
        self.strategy = strategy
        self.next_steps = next_steps

    @abstractmethod
    def process(self, data=None, **kwargs):
        pass

    def _call_next(self, data, **kwargs):
        if self.next_steps is not None:
            self.next_steps.process(data, **kwargs)
        else:
            return data
