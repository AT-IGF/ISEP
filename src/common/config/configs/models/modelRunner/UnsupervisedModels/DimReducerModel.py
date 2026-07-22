from dataclasses import dataclass, field

from src.common.config.configs.models.modelRunner.UnsupervisedModels import (
    UmapModel,
    PcaModel,
)


@dataclass
class DimReducerModel:
    UMAP_REDUCTOR = "umap"
    PCA_REDUCTOR = "pca"

    dim_reducer_to_use: None | str = None

    umap: UmapModel = field(
        default_factory=lambda: UmapModel(
            path=None,
            key=DimReducerModel.UMAP_REDUCTOR,
        )
    )

    pca: PcaModel = field(
        default_factory=lambda: PcaModel(DimReducerModel.PCA_REDUCTOR, components=0)
    )
