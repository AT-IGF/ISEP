from datetime import datetime
import os
from json import load

from dacite import from_dict, Config

from src.core.configurations.ConfigModelBase import ConfigModelBase


class ConfigBase:
    CONFIG_KEY = "config"
    LAST_MODIFY_KEY = "last_modification"

    def __init__(self, configs: list, invalidate_cache_on_save=False):
        self._configs = configs
        self._configs_cache = {}
        self._invalidate_cache_on_save = invalidate_cache_on_save

    @property
    def invalidate_cache_on_save(self):
        return self._invalidate_cache_on_save

    def is_cached(self, config_cls, last_file_modification):
        if config_cls in self._configs_cache.keys():
            if self._invalidate_cache_on_save:
                return False
            return (
                last_file_modification
                == self._configs_cache[config_cls][self.LAST_MODIFY_KEY]
            )
        return False

    def try_get_config(self, config_cls, refresh=False):
        if config_cls not in self._configs:
            raise KeyError("Config does not exist")
        if not issubclass(config_cls, ConfigModelBase):
            raise NotImplementedError("Config does not inherit from ConfigModelBase")

        last_file_modification = os.path.getmtime(config_cls.path())
        if self.is_cached(config_cls, last_file_modification) and refresh == False:
            return self._configs_cache[config_cls][self.CONFIG_KEY]
        else:
            config = self.get_config(config_cls)
            self._configs_cache[config_cls] = {
                self.CONFIG_KEY: config,
                self.LAST_MODIFY_KEY: last_file_modification,
            }

        if config is None:
            raise ValueError("Config cannot be none")

        return config

    def get_config(self, config):
        dict_config = Config(type_hooks={datetime: datetime.fromisoformat})
        with open(config.path(), encoding="utf-8") as f:
            raw_config: dict[dict] = load(f)

            if isinstance(config.config_prop_name, str):
                if config.config_prop_name not in raw_config.keys():
                    raise ValueError(
                        f"Config does contain property: {config.config_prop_name}, "
                        f"if you want to use whole file set 'config_prop_name' property to 'None'"
                    )
                return from_dict(
                    data_class=config,
                    data=raw_config[config.config_prop_name],
                    config=dict_config,
                )

            return from_dict(data_class=config, data=raw_config, config=dict_config)
