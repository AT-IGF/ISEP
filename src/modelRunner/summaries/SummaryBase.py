from abc import ABC
from typing import Generic, TypeVar

T = TypeVar('T')

class SummaryBase(ABC, Generic[T]):
    
    def __init__(self):
        self._message = "Method has to be implemented in the derived class"

    def on_init(self):
        raise NotImplementedError(self._message)

    def on_measurement(self, measurement: T):
        raise NotImplementedError(self._message)

    def summary(self):
        raise NotImplementedError(self._message)