from dataclasses import dataclass, field

from src.common.config.configs.models.common import (
    EarlyStoppingModel,
    LearningRateReducerModel,
)


@dataclass
class TrainParametersModel:
    """Training parameters of the supervised model."""

    OVERSAMPLE_STRATEGY = "OVERSAMPLE"
    """Oversample. Takes effect on cache dataset creation, so it requires generation of a new set."""

    ALING_WEIGHTS_STRATEGY = "ALIGN_WEIGHTS"
    """Align weights."""

    SAMPLING_STRATEGIES = ["OVERSAMPLE", "ALIGN_WEIGHTS"]

    CUSTOM_BUFFER_MODE = "CUSTOM"
    """Custom size, given in ``custom_buffer_size``."""

    ALL_SAMPLES_BUFFER_MODE = "ALL_SAMPLES"
    """All samples."""

    BUFFER_MODES = [CUSTOM_BUFFER_MODE, ALL_SAMPLES_BUFFER_MODE]

    single_type_count: int = 5677
    """Single type count."""

    sampling_strategy: str | None = "ALIGN_WEIGHTS"
    """Sampling strategy. Class imbalance strategy. Note: Oversample requires generation of a new set.
    When not set, no strategy is applied."""

    buffer_size_mode: str | None = ALL_SAMPLES_BUFFER_MODE
    """Buffer size mode. How many samples are loaded into memory and shuffled during training. Too high
    samples count can cause an out of memory exception, however it allows to achieve the best accuracies.
    Lower buffer sizes save memory by loading only data chunks for training. When not set, the default
    buffer size of 50000 is used."""

    custom_buffer_size: int = 25000
    """Buffer size used with the custom buffer size mode."""

    batch_size: int | None = None
    """Training batch size. When not set, the default batch size is used."""

    smoothing: float = 0.1
    """Smoothing. Amount of probability assigned to other labels. Prevents model from being overconfident.
    E.g. having three classes 'A', 'B' and 'C', if a sample is labeled as 'A', setting smoothing at 0.1
    will assign 0.033 probability to 'B' and 'C' and 0.933 to 'A'."""

    epochs: int = 100
    """Epochs. How many times training will be looped."""

    lr: float = 0.001
    """Learning rate. Step size during objective function optimization. When too high, it can leap over
    the optimum; too low causes the search to be too slow. Can be combined with the learning rate
    reducer section."""

    weight_decay: float = 0.001
    """Weight decay. Regularization coefficient to prevent overfitting. Additional penalty for big weights."""

    early_stopping: EarlyStoppingModel = field(
        default_factory=lambda: EarlyStoppingModel(
            enabled=True, min_delta=0, patience=7
        )
    )
    lr_reducer: LearningRateReducerModel = field(
        default_factory=lambda: LearningRateReducerModel(
            enabled=True, patience=5, min_lr=0.00001, min_delta=0.0001, factor=0.1
        )
    )

    def __post_init__(self):
        if (
            self.sampling_strategy != None
            and self.sampling_strategy not in self.SAMPLING_STRATEGIES
        ):
            raise ValueError(
                f"Sampling strategy not found, allowed_values: [{', '.join(self.SAMPLING_STRATEGIES)}] and not set"
            )
