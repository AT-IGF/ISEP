from dataclasses import dataclass, field

from .SizeSummaryModel import SizeSummaryModel


@dataclass()
class SummaryModel:
    run_summaries: bool = False
    test_filter_rel_path: str | None = None
    show_history_plot: bool = False
    evaluate: bool = False
    roc_curve: bool = False
    prec_recall_curve: bool = False
    f1_score: bool = False
    confusion_matrix: bool = False
    thresholds: list[float] = field(default_factory=list)
    size_summary: bool = False
    diff_model_name: str | None = None
