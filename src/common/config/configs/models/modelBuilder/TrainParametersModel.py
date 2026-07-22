from dataclasses import dataclass, field

from src.common.config.configs.models.common import (
    EarlyStoppingModel,
    LearningRateReducerModel,
)


@dataclass
class TrainParametersModel:
    OVERSAMPLE_STRATEGY = "OVERSAMPLE"
    ALING_WEIGHTS_STRATEGY = "ALIGN_WEIGHTS"
    SAMPLING_STRATEGIES = ["OVERSAMPLE", "ALIGN_WEIGHTS"]

    CUSTOM_BUFFER_MODE = "CUSTOM"
    ALL_SAMPLES_BUFFER_MODE = "ALL_SAMPLES"
    BUFFER_MODES = [CUSTOM_BUFFER_MODE, ALL_SAMPLES_BUFFER_MODE]

    run_training: bool = True
    single_type_count: int = 5677
    sampling_strategy: str | None = "ALIGN_WEIGHTS"
    buffer_size_mode: str | None = ALL_SAMPLES_BUFFER_MODE
    custom_buffer_size: int = 25000
    batch_size: int | None = None
    smoothing: float = 0.1
    epochs: int = 100
    lr: float = 0.001
    weight_decay: float = 0.001
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
