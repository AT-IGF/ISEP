from dataclasses import dataclass, fields
from datetime import datetime
from src.common.rawData.features.models.FeatureModel import FeatureModel
from src.common.rawData.Signal import RawData
import numpy as np
from collections.abc import Iterable
import numbers

@dataclass(frozen=True)
class LearnModel:
    feature_models: list[FeatureModel]
    pollen_types: list[str] | None
    
    def is_number_or_nested_list(self, i):
        if isinstance(i, numbers.Number):
            return True
        elif isinstance(i, list) or isinstance(i, np.ndarray):
            return all(self.is_number_or_nested_list(x) for x in i)  # Recursively check all elements
        return False
    
    @staticmethod
    def features_model_as_dict(feature_models, features_to_save):
        learn_model = LearnModel(feature_models=feature_models, pollen_types=None)
        return learn_model.get_feature_models_as_dict(include=features_to_save)
    
    def get_feature_models_as_dict(self, include: list[str]=None):
        result = {}
        for obj in self.feature_models:
            for field in fields(obj):
                key = field.name
                if include != None:
                    if key not in include:
                        continue
                    
                value = getattr(obj, key)
                if isinstance(value, datetime):
                    value = np.datetime64(value, "us")
                    value = value.astype('int64')
                if isinstance(value, RawData):
                    continue
                if isinstance(value, str):  # Check if it's a string type
                    value = value.encode('utf-8')
                result.setdefault(key, []).append(value)
        return result