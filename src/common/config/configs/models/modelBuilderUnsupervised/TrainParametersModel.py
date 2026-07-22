from dataclasses import dataclass, field
from src.core import ListHelper
from src.common.tensorflow import InputModelNames
from src.common.config.configs.models.common import (
    EarlyStoppingModel,
    LearningRateReducerModel,
)


@dataclass
class TrainParametersModel:
    pollen_types_binaries_paths: list[str] = field(default_factory=list)
    learningModels: list[str] = field(default_factory=list[str])
    pollen_types: list = field(default_factory=list)
    train_model: bool = True

    pollen_types_cache_rel_path: str | None = "unsupervised/cache"
    filter_rel_path: str | None = "common/filters/should_append_unlabeled3.py"
    scaler_path: str | None = None
    validation_set_size: float = 0.2
    with_labeled_samples: bool = False

    epochs: int = 150
    lr: float = 0.001
    weight_decay: float = 0.004

    early_stopping: EarlyStoppingModel = field(
        default_factory=lambda: EarlyStoppingModel(
            enabled=True, min_delta=0, patience=8
        )
    )
    lr_reducer: LearningRateReducerModel = field(
        default_factory=lambda: LearningRateReducerModel(
            enabled=True, patience=4, min_lr=7e-6, min_delta=0.0001, factor=0.5
        )
    )

    def __post_init__(self):
        not_found_models = ListHelper.remove_elements(
            self.learningModels, InputModelNames.LEARNING_MODELS
        )
        if len(not_found_models) != 0:
            raise NotImplementedError(
                f"Input modalities not found={not_found_models}, available modalities={InputModelNames.LEARNING_MODELS}"
            )

        if self.validation_set_size > 1 or self.validation_set_size < 0:
            raise ValueError("validation_set_size must be between 0-1")
