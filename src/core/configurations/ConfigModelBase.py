from abc import ABC, abstractmethod


class ConfigModelBase(ABC):
    @property
    def config_prop_name(self) -> str | None:
        return None

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError("Config path is not defined")

    @property
    @abstractmethod
    def module_name(self) -> str:
        raise NotImplementedError("Config path is not defined")
