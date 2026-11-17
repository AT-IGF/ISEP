from dataclasses import dataclass, field

from .SizeSummaryModel import SizeSummaryModel


@dataclass()
class SummaryModel:
    """Evaluation summaries of the trained model."""

    run_summaries: bool = False
    """Run summaries. Trained model performance on the test set."""

    test_filter_rel_path: str | None = None
    """Particle filter applied to the test set, relative to the resources directory."""

    show_history_plot: bool = False

    evaluate: bool = False
    """Evaluate model. Display in console model computed losses and accuracy on the test set."""

    roc_curve: bool = False
    """ROC curve. Receiver Operating Characteristic curve, plots sensitivity against false positive rate."""

    prec_recall_curve: bool = False
    """Precision recall curve. Plots prediction precision against the recall."""

    f1_score: bool = False
    """F-1 score curve. Harmonic mean of precision and recall showing the best tradeoff between precision
    and recall."""

    confusion_matrix: bool = False
    """Confusion matrix. Plots per-class performance of the trained model."""

    thresholds: list[float] = field(default_factory=list)
    """Thresholds. Prints characteristics like f1, precision, recall and samples count left for specific
    threshold. When only one threshold is set, shows an additional confusion matrix for given results."""

    size_summary: bool = False
    """Size summary. Shows size histogram on the train set."""

    diff_model_name: str | None = None
    """Compare against another model. Name of the model to compare the currently trained model with.
    Note: to compare models, they have to be trained on the same input modalities and the same pollen
    types (ordered in the same way). Note 2: compared models should use the same test set, i.e. the same
    cache files namespace (``test_model_name``)."""
