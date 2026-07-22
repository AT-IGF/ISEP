from dataclasses import dataclass, field
from src.core import ConfigModelBase, PathHelper

from src.common import Consts
from src.common.config.configs.models.predictionsMapper import (
    SplitTimespanModel,
    ThresholdsModel,
    PlotSettingsModel,
    PreviewModel,
)


@dataclass()
class PredictionsMapperConfig(ConfigModelBase):

    file_to_process_rel_path: str | None = None
    save_path_rel_path: str = "predictionsMapper/out"
    split_timespan: SplitTimespanModel = field(default_factory=SplitTimespanModel)
    pollen_types: list[str] = field(default_factory=list)
    thresholds: ThresholdsModel = field(default_factory=ThresholdsModel)
    plot_settings: PlotSettingsModel = field(default_factory=PlotSettingsModel)
    preview: PreviewModel = field(default_factory=PreviewModel)
    config_prop_name = "predictionsMapper"
    module_name = "predictionsMapper"

    @staticmethod
    def path():
        return PathHelper.join_rel_path(
            Consts.RESOURCES_PATH, "/predictionsMapper/config.json"
        )

    def get_file_to_process_path(self):
        return PathHelper.get_absolute_path(
            Consts.RESOURCES_PATH,
            self.file_to_process_rel_path,
            raise_message="File to process path has to be set",
        )
