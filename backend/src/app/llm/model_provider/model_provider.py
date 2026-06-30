from typing import Protocol


class ModelProvider(Protocol):

    def __init__(self, model_name: str):
        self.model_name = model_name

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"'{key}' not found in {self.__class__.__name__}")

