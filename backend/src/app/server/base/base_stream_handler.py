from abc import ABC, abstractmethod


class BaseStreamHandler(ABC):

    @abstractmethod
    def handle_stream(self, stream,**kwargs):
        pass