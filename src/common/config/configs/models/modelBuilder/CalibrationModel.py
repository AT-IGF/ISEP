from dataclasses import dataclass


@dataclass
class CalibrationModel:
    """Temperature scaling calibration of the trained model."""

    MODEL_EXTENSION = "keras"
    CLASS_EVALUATION = "CLASS"
    """Class wise."""

    ALL_EVALUATION = "ALL"
    """Top label."""

    run_calibration: bool = False
    """Run calibration. Calibrate the trained model with the use of temperature scaling. A temperature is
    learned for every class, and the output logits are divided by it before softmax. The calibrated model
    is saved as ``<model_save_name>_model_calibrated.keras``."""

    overwrite_model: bool = False
    """Overwrite if exists."""

    epochs: int = 30
    """Epochs. How many times training will be looped."""

    lr: float = 0.1
    """Learning rate. Step size during objective function optimization. When too high, it can leap over
    the optimum; too low causes the search to be too slow."""

    evaluate_calibration: bool = True
    """Evaluate calibration. Divides predictions into bins and compares the mean predicted probability
    (conf) with the ratio of true labels (acc). E.g. acc = 0.35, conf = 0.4 means the model is
    overconfident."""

    evaluation_mode: str = ALL_EVALUATION
    """Evaluation mode. Class wise - accuracy for specific label confidence. Top label - accuracy for
    top label confidence."""

    reliability_mode: str = ALL_EVALUATION
    """Reliability curves mode. Class wise - plots for every class, how reliable particular class
    prediction is. Top label - selected class with the highest prediction."""

    plot_reliability_curves: bool = True
    """Plot reliability curves. Indicates how reliable the model is. If below the XY line - overconfident,
    above - underconfident."""

    plot_temp_changes: bool = True
    """Plot temperature changes. Plots temperature changes during training."""

    plot_probability_distributions: bool = True
    """Plot probability distributions. Shows how max label probabilities are distributed before and after
    calibration. As a rule of thumb, the more samples to the right, the better. Note: these are
    probabilities, not accuracies; a model can be confident and still predict wrong."""
