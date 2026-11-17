from dataclasses import dataclass, field
from src.core import ListHelper
from src.common.tensorflow import InputModelNames
from src.common.config.configs.models.common import (
    EarlyStoppingModel,
    LearningRateReducerModel,
)


@dataclass
class TrainParametersModel:
    """Data and training parameters of the autoencoder."""

    InputModelNames = InputModelNames

    pollen_types_binaries_paths: list[str] = field(default_factory=list)
    """Samples directories. Every subdirectory of the given paths is read as a separate set of samples.
    With ``with_labeled_samples`` enabled, subdirectories named as one of ``pollen_types`` are treated
    as labeled, the remaining ones as unlabeled."""

    learningModels: list[str] = field(default_factory=list[str])
    """Input modalities. Model inputs used for training and further for prediction purposes. Size modality
    is calculated based on the scattering, no additional input is needed."""

    pollen_types: list = field(default_factory=list)
    """Pollen types of the labeled samples, used with ``with_labeled_samples``. The order defines the
    label index of every type."""

    train_model: bool = True
    """Run training."""

    pollen_types_cache_rel_path: str | None = "unsupervised/cache"
    """Processed files cache dir. Place in which train and validation sets will be saved. Cache is saved
    in the subdirectory named after the selected filter."""

    filter_rel_path: str | None = None
    """Filter path. Path to the file that will be used for samples filtration. Example filters are
    available in *resources/common/filters*. Note: for best match the same filter should be used for
    both the scaler and the trained model."""

    scaler_path: str | None = None
    """Scaler path. Fitted scaler file path, relative to the resources directory. Required for training."""

    validation_set_size: float = 0.2
    """Validation set size, as a fraction between 0 and 1."""

    with_labeled_samples: bool = False
    """Dataset partially labeled. When selected, directories named as one of ``pollen_types`` are labeled
    and used for comparison in verification and clustering. Labels are not used in training."""

    epochs: int = 150
    """Epochs. How many times training will be looped."""

    lr: float = 0.001
    """Learning rate. Step size during objective function optimization. When too high, it can leap over
    the optimum; too low causes the search to be too slow. Can be combined with the learning rate
    reducer section."""

    weight_decay: float = 0.004
    """Weight decay. Regularization coefficient to prevent overfitting. Additional penalty for big weights."""

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
