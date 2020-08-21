from abc import ABC, abstractmethod


class ServerInterface(ABC):
    @abstractmethod
    def get_name(self) -> str:
        return ""

    @abstractmethod
    def connect(self):
        return False

    @abstractmethod
    def disconnect(self):
        return False

    @abstractmethod
    def is_connected(self) -> bool:
        return False

    @abstractmethod
    def read(self):
        return ''

    @abstractmethod
    def write(self, message):
        pass
