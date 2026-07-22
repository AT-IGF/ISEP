from abc import ABC, abstractmethod
import tensorflow as tf

class TfParserBase(ABC):
    @abstractmethod
    def _parse_function(self, proto) -> list[str]:
        raise NotImplementedError("Parse function has to be implemented")

    @staticmethod
    def to_decoder_name(name, suffix=""):
        return name + suffix