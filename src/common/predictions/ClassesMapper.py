from dataclasses import asdict
import logging
from src.common.predictions.models import ClassesMetadataModel, MappingType


def prediction_to_classes(y_pred: list[float], classes: list[str], metadata: ClassesMetadataModel = None, mapping_type: MappingType = MappingType.PERCENTAGE):
    if len(classes) != len(y_pred):
        raise ValueError(f"Given pollen types count={len(classes)} does not match predicted pollen types count={len(y_pred)} \n" +
                         f"Pollen types to match with=[{classes}]")
    
    pred_dict: dict = {}
    if metadata:
        pred_dict = asdict(metadata)
    
    formatting = "{:.2}"
    if mapping_type == MappingType.ARG_MAX:    
        y_pred = to_argmax(y_pred)
        formatting = "{:d}"
    
    for idx, pollen_type in enumerate(classes):
        pred_dict[pollen_type] = formatting.format(y_pred[idx])

    return pred_dict

def to_argmax(y_pred: list[float]):
    import numpy as np
    y_preds_len = len(y_pred)
    arg_max_idx = np.array(y_pred).argmax(axis=0)
    
    result = np.zeros(y_preds_len, dtype=np.int8)
    result[arg_max_idx] = 1
    
    return result
