import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

from src.common import get_pollen_type_idx
from src.common.config.Config import Config
from src.common.config.configs.TypesConfig import TypesConfig
from src.common.rawData.Signal.RawData import RawData
from src.common.rawData.features.models.FeatureModel import FeatureModel
from src.common.tensorflow import InputModelNames
from sklearn.preprocessing import MinMaxScaler


class FeaturesHandler:
    def __init__(self, pollen_types: list[str] | None, scattering_cutoff: int) -> None:
        """not setting 'pollen_types' means that type is unkown"""
        self._is_type_unknown = True if pollen_types == None else len(pollen_types) == 0
        self._pollen_types = pollen_types
        self._scattering_cutoff = scattering_cutoff

    def get_feature_models_unsupervised(self, raw_data: list[RawData], scaler=None):
        models: list[FeatureModel] = []
        raw_data_len = 0
        for idx, temp_sample in enumerate(raw_data):
            raw_data_len += 1
            raw_dict = temp_sample.to_unsup_input_name_dict(self._scattering_cutoff)
            if scaler is not None:
                scaler.incremental_scaler_fit(arrays_dict=raw_dict)

            model: FeatureModel = self.get_feature_model_to_normalize(
                raw_dict=raw_dict, raw_data=temp_sample
            )
            if model is None:
                continue
            models.append(model)

        if len(raw_data) != len(models):
            logging.getLogger().warning(
                f"Some additional particles were removed within featureHandler, raw_data_count={raw_data_len}, feature_models_count={len(models)}"
            )
        return models

    def get_feature_model_to_normalize(self, raw_dict: dict, raw_data: RawData):
        type_idx = -1
        if not self._is_type_unknown:
            type_idx = get_pollen_type_idx(self._pollen_types, raw_data.type)

        model = FeatureModel(
            lifetime=raw_dict[InputModelNames.LIFETIME],
            lifetime_unsup=raw_dict[InputModelNames.LIFETIME_UNSUP],
            scattering=raw_dict[InputModelNames.SCATTERING],
            scattering_unsup=raw_dict[InputModelNames.SCATTERING_UNSUP],
            spectrum=raw_dict[InputModelNames.SPECTRUM],
            spectrum_unsup=raw_dict[InputModelNames.SPECTRUM_UNSUP],
            size=raw_dict[InputModelNames.SIZE],
            type=raw_data.type,
            type_idx=type_idx,
            time=raw_dict[InputModelNames.TIME_UNSUP],
            raw_data=raw_data,
        )

        return model

    def get_feature_model_scaled(self, raw_data: RawData):
        type_idx = -1
        if not self._is_type_unknown:
            type_idx = get_pollen_type_idx(self._pollen_types, raw_data.type)

        model = FeatureModel(
            lifetime=raw_data[InputModelNames.LIFETIME],
            lifetime_unsup=raw_data[InputModelNames.LIFETIME_UNSUP],
            scattering=raw_data[InputModelNames.SCATTERING],
            scattering_unsup=raw_data[InputModelNames.SCATTERING_UNSUP],
            spectrum=raw_data[InputModelNames.SPECTRUM],
            spectrum_unsup=raw_data[InputModelNames.SPECTRUM_UNSUP],
            size=raw_data[InputModelNames.SIZE],
            type=raw_data.type,
            type_idx=type_idx,
            time=raw_data[InputModelNames.TIME_UNSUP],
            raw_data=raw_data,
        )

        return model
