from datetime import datetime

import numpy as np
from src.common.sampler.RawDataBase import RawDataBase
from src.common.sampler import get_particle_size
from src.core import File

from .RawDataValidator import validate
from .RawDataKeys import (
    VAL_SCATTERING,
    VAL_SCATTERING_IMAGE,
    VAL_SPECTROMETER,
    VAL_LIFETIME,
    VAL_TIMESTAMP,
)


def to_raw_data_model(raw_data: list[dict], file: File) -> list:
    from .RawData import RawData
    raw_data_list: list[RawData] = []
    for data in raw_data:
        validate(data)
        raw_data_model = map_to_raw_data(data, file)
        raw_data_list.append(raw_data_model)

    return raw_data_list


def map_to_raw_data(data: RawDataBase, file: File):
    from .RawData import RawData
    if isinstance(data.time, datetime):
        dt = data.time
    else:
        dt = datetime.strptime(data.time, "%Y-%m-%d %H:%M:%S.%f")
    
    return RawData(
        scattering=np.array(data.scattering),
        spectrometer=np.array(data.spectrometer),
        lifetime=np.array(data.lifetime),
        time=dt,
        file=file,
        type=get_pollen_type_from_path(file.path),
        size=np.float32(get_particle_size(data.scattering)),
    )


def get_pollen_type_from_path(path: str):
    if "\\" in path:
        return path.split("\\")[-1]
    return path.split("/")[-1]
