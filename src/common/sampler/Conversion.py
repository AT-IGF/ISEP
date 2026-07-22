import gzip
import os
from pathlib import Path
import pickle
from typing import Generator

from src.core.files.models import File
import src.common.sampler.RawDataBase as _rdb
import sys
sys.modules['RawDataBase'] = _rdb
from src.common.rawData.Signal.RawDataAdapter import map_to_raw_data

def load_data(filepath: str | Path) -> list[_rdb.RawDataBase]:
    with gzip.open(filepath, 'rb') as f:
        return pickle.load(f)


def convert(path, should_append_callback, raw_data_models_from_file_count: int):
    raw_data_base_list = load_data(path)
    data = []
    for raw_data_base in raw_data_base_list:
        raw_data = map_to_raw_data(raw_data_base, file=File(path=path))
        should_add, raw_data = should_append_callback(raw_data)
        if should_add:
            data.append(raw_data)
        if len(data) == raw_data_models_from_file_count:
            break
    return data
