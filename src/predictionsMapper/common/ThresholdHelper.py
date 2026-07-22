from src.common.config.configs.models.predictionsMapper.ThresholdsModel import (
    ThresholdsModel,
)


def get_threshold(thresholds: ThresholdsModel, p_type):
    if (
        thresholds.threshold_type == thresholds.CLASS_THRESHOLD
        and p_type in thresholds.get_thresholds()
    ):
        return thresholds.get_thresholds()[p_type]
    return thresholds.threshold
