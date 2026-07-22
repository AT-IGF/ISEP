#  Created by:
#  mgr Artur Tomczak (artur.tomczak@fuw.edu.pl)
#  Intitute of Geophysiscs, Faculty of Physics, University of Warsaw

import logging
import sys
import os
import datetime

from logging import Logger as _Logger

from src.core.logger.StreamToLogger import StreamToLogger
from src.core.logger.themes import ColoredFormatter
from src.core.path.PathHelper import PathHelper


class Logger:
    @staticmethod
    def init_logger(logger_name=None):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        return logger

    @staticmethod
    def get_formatter():
        return logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    @staticmethod
    def get_stdout_handler(formatter=None):
        if formatter is None:
            formatter = ColoredFormatter()
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        return stdout_handler

    @staticmethod
    def get_file_handler(path: str):
        formatter = Logger.get_formatter()
        current_time = datetime.datetime.now().strftime("%Y%m%d")
        filename = current_time + ".log"
        path = PathHelper.join_path(path, filename)

        if not os.path.isabs(path):
            path = os.path.relpath(str.format(path))

        file_handler = logging.FileHandler(path, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        return file_handler, path

    @staticmethod
    def GetLogger(path: str, formatter=None):
        logger: _Logger = Logger.init_logger()
        stdout_handler = Logger.get_stdout_handler(formatter)
        file_handler, _ = Logger.get_file_handler(path)

        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

        return logger

    @staticmethod
    def CreateLoggerByFile(file, path: str, append_steam=False):
        file_dir = os.path.dirname(os.path.realpath(file))
        path = PathHelper.join_rel_path(file_dir, path)
        Logger.CreateLoggerFromPath(path, append_steam)

    @staticmethod
    def CreateLoggerFromPath(path: str, append_steam=False, logger_name=None):
        if not os.path.exists(path):
            os.makedirs(path)

        logger: _Logger = Logger.init_logger(logger_name)
        stdout_handler = Logger.get_stdout_handler()
        file_handler, file_path = Logger.get_file_handler(path)

        logger.addHandler(file_handler)
        logger.addHandler(stdout_handler)

        if append_steam:
            Logger.with_sys_out(logger)

        logger.info(f"Logging in: '{file_path}'")

        return logger

    @staticmethod
    def with_sys_out(logger):
        sys.stdout = StreamToLogger(logger, logging.INFO)
        sys.stderr = StreamToLogger(logger, logging.ERROR)
