from pathlib import Path

import pandas as pd
import pytest
from src.common import Consts
from src.common.config import Config
from src.common.config.configs import ModelBuilderConfig, TypesConfig, PathsConfig, ModelBuilderUnsupervisedConfig, ModelRunnerConfig, ModelBuilderScalerConfig, PredictionsMapperConfig, AllParticlesAvgsConfig
from tests.end_to_end.utils.SequentialPool import SequentialPool
from src.common.tensorflow import InputModelNames

@pytest.mark.parametrize("metric_to_process, plot_name, is_hist, is_plot", [
    (InputModelNames.SPECTRUM, "spectras", True, True),
    (InputModelNames.LIFETIME, "lifetime", True, True),
    (InputModelNames.SCATTERING, "scatterings", True, False),
    (InputModelNames.SIZE, "sizes", True, False),
])
def test_handle_when_run_displays_aggregated_summaries(monkeypatch, test_resources, metric_to_process, plot_name, is_hist, is_plot):
    # arrange
    hist_plot = test_resources /  "plots" / f"hist_{plot_name}_1.png"
    plot_plot = test_resources /  "plots" / f"plot_{plot_name}_1.png"

    model_builder_config = ModelBuilderConfig()
    model_builder_config.run_training = True
    model_builder_config.binary_paths = (
        Path(__file__).resolve().parent.parent
        / "resources"
        / "binary_paths"
    )
    
    monkeypatch.setattr(
        Consts,
        "RESOURCES_PATH",
        str(test_resources)
    )
    
    types_config = TypesConfig()
    types_config.pollen_types = ["Alnus", "ArrhinateRum"]
    paths_config = PathsConfig()
    paths_config.zip_files_rel_path = "binary_paths"
    model_builder_unsup_config = ModelBuilderUnsupervisedConfig()
    model_builder_scaler_config = ModelBuilderScalerConfig()
    model_runner_config = ModelRunnerConfig()
    predictions_mapper_config = PredictionsMapperConfig()
    all_particles_avgs_config = AllParticlesAvgsConfig()
    all_particles_avgs_config.pollen_types = ["Alnus", "ArrhinateRum"]
    all_particles_avgs_config.metric_to_process = metric_to_process
    all_particles_avgs_config.lifetime.histogram.plot = True
    all_particles_avgs_config.lifetime.plot_combined.plot = True
    all_particles_avgs_config.scattering.histogram.plot = True
    all_particles_avgs_config.scattering.histogram.plot = True
    all_particles_avgs_config.spectrum.histogram.plot = True
    all_particles_avgs_config.spectrum.plot_combined.plot = True
    all_particles_avgs_config.size.histogram.plot = True
    
    def fake_get(config, refresh=False):
        if config is ModelBuilderConfig:
            return model_builder_config

        if config is TypesConfig:
            return types_config

        if config is PathsConfig:
            return paths_config
        
        if config is ModelBuilderUnsupervisedConfig:
            return model_builder_unsup_config
        
        if config is ModelBuilderScalerConfig:
            return model_builder_scaler_config
        
        if config is ModelRunnerConfig:
            return model_runner_config
        
        if config is PredictionsMapperConfig:
            return predictions_mapper_config
        
        if config is AllParticlesAvgsConfig:
            return all_particles_avgs_config

        raise ValueError(f"Unexpected config: {config}")

    monkeypatch.setattr(
        Config,
        "get",
        staticmethod(fake_get)
    )

    from src.common.rawData import RawDataHanlder
    monkeypatch.setattr(
        RawDataHanlder.multiprocessing,
        "Pool",
        SequentialPool
    )
    
    # act
    from src.dataViewer import AllParticlesAvgs
    AllParticlesAvgs.handle()

    # assert
    if is_hist:
        assert hist_plot.is_file(), f"Output plot was not created: {hist_plot}"
    if is_plot:
        assert plot_plot.is_file(), f"Output plot was not created: {plot_plot}"
    