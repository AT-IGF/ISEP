import json
import logging
import os
from pathlib import Path
import sys

from src.core.parsers.stringParsers.Strings import is_blank
from src.common import Consts
from src.core import PathHelper
from varname import nameof

def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = Path(__file__).resolve().parents[2]
    return os.path.join(base, relative_path)

def get_default_resources_path():
    return PathHelper.join_path(Path(__file__).resolve().parent.parent.parent, "resources")
    
def load_all_consts(json_data: dict):
    for key in json_data:
        if hasattr(Consts, key):
            value = json_data[key]
            if key == nameof(Consts.RESOURCES_PATH) and is_blank(value):
                value = get_default_resources_path()
                logging.info(f"{nameof(Consts.RESOURCES_PATH)} was not set default will be taken: {value}")
                
            setattr(Consts, key, value)


def log_consts(message, logger_name=None):
    log = logging.getLogger(logger_name)
    log.info("=" * 50)
    log.info(message)
    log.info("-" * 50)
    for key, value in vars(Consts).items():
        if not key.startswith("_"):
            log.info(f"  {key:30s} : {value}")
    log.info("=" * 50)


def override_config_log(logger_name=None):
    consts_settings_path = resource_path("resources/config.json")
    if PathHelper.is_file(consts_settings_path):
        with open(consts_settings_path, "r") as f:
            settings = json.load(f)
            load_all_consts(settings)
        log_consts("Application configuration loaded:", logger_name)
    else:
        logging.getLogger(logger_name).info(
            f"Application configuration NOT loaded, path does not exists, path: {consts_settings_path}"
        )
        log_consts("Application configuration defaults:", logger_name)


def override_config():
    consts_settings_path = resource_path("resources/config.json")
    if PathHelper.is_file(consts_settings_path):
        with open(consts_settings_path, "r") as f:
            settings = json.load(f)
            load_all_consts(settings)
