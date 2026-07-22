import numpy as np

def is_any_pred_within_threshold(y_pred: list[float], threshold: float):
    return np.max(y_pred) >= threshold

def get_preds_above_threshold(y_preds: list[list[float]], threshold: float):
    y_pred_threshold: list[list[float]] = []
    for y_pred in y_preds:
        if is_any_pred_within_threshold(y_pred, threshold):
            y_pred_threshold.append(y_pred)
    return y_pred_threshold