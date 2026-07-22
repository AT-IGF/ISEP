from dataclasses import dataclass


@dataclass
class CalibrationModel:
    MODEL_EXTENSION = "keras"
    CLASS_EVALUATION = "CLASS"
    ALL_EVALUATION = "ALL"

    run_calibration: bool = False
    overwrite_model: bool = False
    epochs: int = 30
    lr: float = 0.1
    evaluate_calibration: bool = True
    evaluation_mode: str = ALL_EVALUATION
    reliability_mode: str = ALL_EVALUATION
    plot_reliability_curves: bool = True
    plot_temp_changes: bool = True
    plot_probability_distributions: bool = True
