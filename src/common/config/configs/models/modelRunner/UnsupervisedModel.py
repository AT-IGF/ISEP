from dataclasses import dataclass, field

from src.common.config.configs.models.modelRunner.UnsupervisedModels.ClustererModel import (
    ClustererModel,
)
from src.common.config.configs.models.modelRunner.UnsupervisedModels.DimReducerModel import (
    DimReducerModel,
)


@dataclass
class UnsupervisedModel:
    """Cluster filtering of supervised predictions with models from unsupervised training (experimental)."""

    run_unsupervised: bool = False
    """Cluster filtering. Optional. Uses output models from the unsupervised training to remove particles
    whose cluster is not mapped to their predicted pollen type."""

    autoencoder_path: str | None = None
    """Autoencoder path. Path to the trained autoencoder from the unsupervised training."""

    dim_reducer: DimReducerModel = field(default_factory=DimReducerModel)
    clusterer: ClustererModel = field(default_factory=ClustererModel)
