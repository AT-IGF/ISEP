from dataclasses import dataclass


@dataclass
class SummaryDataFrameModel:
    threshold: float
    loss: float
    accuracy: float
    precission: float
    recall: float
    f1: float
    pollen_types: list[str]
    pred_summary: dict
    no_threshold_count: int
    threshold_count: int