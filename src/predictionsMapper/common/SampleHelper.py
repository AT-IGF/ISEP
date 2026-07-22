import pandas as pd

from src.predictionsMapper.common.Consts import RAPID_E_LITERS_PER_MINUTE


def calculate_p_per_m3(col: pd.DataFrame, span) -> pd.Series:
    total_minutes = (
        span.days * 1440 + span.hours * 60 + span.minutes + span.seconds / 60
    )
    if total_minutes <= 0:
        raise ValueError("Total sampling time must be > 0")

    volume_m3 = RAPID_E_LITERS_PER_MINUTE * total_minutes * 0.001

    return col / volume_m3
