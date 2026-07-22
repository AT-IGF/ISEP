from dataclasses import dataclass, field

from src.common.config.configs.models.modelRunner.UnsupervisedModels.ClustererModel import (
    ClustererModel,
)
from src.common.config.configs.models.modelRunner.UnsupervisedModels.DimReducerModel import (
    DimReducerModel,
)


@dataclass
class UnsupervisedModel:
    run_unsupervised: bool = False
    autoencoder_path: str | None = None
    dim_reducer: DimReducerModel = field(default_factory=DimReducerModel)
    clusterer: ClustererModel = field(default_factory=ClustererModel)
