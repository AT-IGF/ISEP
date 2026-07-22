from pathlib import Path

import numpy as np

from sample.pklConverter.models.RawDataBase import RawDataBase


class Converter:
    VAL_SCATTERING = "Scattering"
    VAL_SCATTERING_IMAGE = "Image"
    VAL_SPECTROMETER = "Spectrometer"
    VAL_LIFETIME = "Lifetime"
    VAL_TIMESTAMP = "Timestamp"
    
    def __init__(self, ):
        pass
    
    # def map(self, data: dict):
    #     return RawDataBase(
    #         scattering=np.array(data[self.VAL_SCATTERING][self.VAL_SCATTERING_IMAGE]),
    #         spectrometer=np.array(data[self.VAL_SPECTROMETER]),
    #         lifetime=np.array(data[self.VAL_LIFETIME]),
    #         time=data[self.VAL_TIMESTAMP],
    #     )
    
    def map_to_raw_data(self, filename: Path) -> list[RawDataBase]:
        # read measurement file
        # map to list of RawDataBase
        # return the list
        raise NotImplementedError("Measurement file mapping is not implemented")