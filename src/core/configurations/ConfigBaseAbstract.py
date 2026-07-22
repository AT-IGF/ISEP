from abc import ABC, abstractmethod
from typing import TypeVar


class ConfigBaseAbstract(ABC):
    T = TypeVar('T')

    @property
    @abstractmethod
    def configs(self) -> dict:
        pass

    @property
    @abstractmethod
    def config_base(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def get(config: T) -> T:
        pass

