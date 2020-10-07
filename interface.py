from abc import ABC, abstractmethod
from datetime import datetime


class ServerInterface(ABC):
    @abstractmethod
    def get_name(self) -> str:
        return ""

    @abstractmethod
    def get_tags(self) -> dict:
        return {}

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

    def format_data(self, data):
        # return format(f'data from {self.get_name()} at {datetime.now()}: {data}')
        return data