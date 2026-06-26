from abc import ABC, abstractmethod


class BaseCheckpointer(ABC):

    @abstractmethod
    def create_checkpoint(self, *args, **kwargs):
        pass
