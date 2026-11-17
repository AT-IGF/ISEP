from varname import nameof
from dataclasses import asdict, is_dataclass
import os
import sys

from src.core.path import PathHelper
from src.common import override_config
from src.common import (
    DataViewerConfig,
    AllParticlesAvgsConfig,
    ModelBuilderScalerConfig,
    ModelBuilderConfig,
    ModelBuilderUnsupervisedConfig,
    ModelRunnerConfig,
    PredictionsMapperConfig,
)


def _setup_matplotlib():
    """Interactive windows in scripts, inline plots in notebooks, no windows on headless machines."""
    import matplotlib
    import matplotlib.pyplot as plt

    if "ipykernel" in sys.modules:
        return  # keep the notebook backend (inline or widget)
    if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
        matplotlib.use("Agg")  # no display: plots are only saved
        return
    matplotlib.use("TkAgg")
    plt.rcParams["figure.figsize"] = (19.2, 10.8)
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = 100


def _run(task, primary=None, *configs, **kwargs):
    """Run an ISEP module with optional configuration overrides."""
    override_config()
    import logging

    root = logging.getLogger()
    root.handlers[:] = (
        []
    )  # every task sets up its own handlers; prevents duplicated log lines
    root.filters[:] = []

    _setup_matplotlib()

    for config in configs:
        generate_config(type(config), **asdict(config))
    generate_config(primary, **kwargs)

    return task()


def generate_config(config, **kwargs):
    from pathlib import Path
    import json
    from src.core import write_data, AccessType

    path = Path(config.path())
    config_data = None
    data = {}
    clean_config = config()
    if PathHelper.is_file_exists(path):
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
        if clean_config.config_prop_name in data:
            config_data = data[config.config_prop_name]

    if config_data is None:
        config_data = asdict(clean_config)
        data[config.config_prop_name] = config_data

    def json_serializer(obj):
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    _config = {
        **config_data,
        **kwargs,
    }

    data[clean_config.config_prop_name] = _config

    data = json.dumps(data, indent=4, default=json_serializer)
    write_data(clean_config.path(), data, access_type=AccessType.Write)


def plot_single_sample(*configs, **kwargs):
    from src.dataViewer.DataViewer import handle as _plot_single_sample

    return _run(_plot_single_sample, DataViewerConfig, *configs, **kwargs)


def plot_aggregated_samples(*configs, **kwargs):
    from src.dataViewer.AllParticlesAvgs import handle as _plot_aggregated_samples

    return _run(_plot_aggregated_samples, AllParticlesAvgsConfig, *configs, **kwargs)


def scale_model_data(*configs, **kwargs):
    from src.modelBuilder.ModelBuilderDataScaler import handle as _scale_model_data

    return _run(_scale_model_data, ModelBuilderScalerConfig, *configs, **kwargs)


def train_supervised_model(*configs, **kwargs):
    from src.modelBuilder.ModelBuilder import handle as _train_supervised_model

    return _run(_train_supervised_model, ModelBuilderConfig, *configs, **kwargs)


def train_unsupervised_model(*configs, **kwargs):
    from src.modelBuilder.ModelBuilderUnsupervided import (
        handle as _train_unsupervised_model,
    )

    return _run(
        _train_unsupervised_model, ModelBuilderUnsupervisedConfig, *configs, **kwargs
    )


def run_predictions(*configs, **kwargs):
    from src.modelRunner.ModelRunner import handle as _run_predictions

    return _run(_run_predictions, ModelRunnerConfig, *configs, **kwargs)


def map_predictions(*configs, **kwargs):
    from src.predictionsMapper.PredictionsMapper import handle as _map_predictions

    return _run(_map_predictions, PredictionsMapperConfig, *configs, **kwargs)


__all__ = [
    nameof(plot_single_sample),
    nameof(plot_aggregated_samples),
    nameof(scale_model_data),
    nameof(train_supervised_model),
    nameof(train_unsupervised_model),
    nameof(run_predictions),
    nameof(map_predictions),
]
