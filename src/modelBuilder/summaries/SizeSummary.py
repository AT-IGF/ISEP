import logging

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

from src.core.plots.plotting_utils import plt_show
from src.modelBuilder.keras.models import TrainedModel
from src.modelBuilder.keras.helpers import TfrecordGenerator
from src.common.config.configs import TypesConfig
from src.common.config import Config, ModelBuilderConfig
from src.modelBuilder.datasetHandler.models import DatasetSplitModel
from src.common.tensorflow.InputModelNames import SIZE
from src.modelBuilder.keras.helpers.TfRecordParsers import SupervisedTfParser
from src.common import Consts


class SizeSummary:

    def __init__(self) -> None:
        self._logger = logging.getLogger()
        self._config = Config.get(ModelBuilderConfig)
        self.summaries_config = Config.get(ModelBuilderConfig).summaries

    def is_summary_available(self, sets_names: list[str]):
        if self.summaries_config.size_summary == False:
            self._logger.info(
                "Size summary is set to False, setup it in configuration tu run size summaries"
            )
            return False

        if SIZE not in sets_names:
            self._logger.info(
                f"Size summary unavailable, model has not been trained based on size. Input modalities={self._config.learningModels}. "
                + f"To configure it add '{SIZE}' to the list under learningModels section"
            )
            return False

        return True

    def summary(self, tained_model: TrainedModel, scalers):
        if SIZE not in self._config.learningModels:
            return

        self._logger.info(
            f"Running size summary. To turn it off remove section 'size_summary' from config file"
        )
        train_sizes = list(
            tained_model.dataset.get_train_dataset(
                repeat=False, parse_function=SupervisedTfParser._size_parse_function
            ).as_numpy_iterator()
        )
        train_labels = list(
            tained_model.dataset.get_train_dataset(
                repeat=False, parse_function=SupervisedTfParser._labels_parse_function
            ).as_numpy_iterator()
        )
        train_sizes = np.concatenate(train_sizes)
        train_labels = np.concatenate(train_labels)
        renormalized_train_sizes = (
            scalers[SIZE].inverse_transform(train_sizes.reshape(-1, 1)).flatten()
        )

        # plt.hist(renormalized_train_sizes, bins=100, histtype="bar", facecolor = '#2ab0ff', edgecolor='#169acf', linewidth=0.5, label="Total")
        plt.xticks(np.arange(0, 105, 5), rotation=45)
        plt.xlim(0, 100)

        typesConfig = Config.get(TypesConfig)
        for idx, type_ in enumerate(typesConfig.pollen_types):
            self.plot_particle_type(
                y_train=train_labels,
                train_sizes=train_sizes,
                particle_type=type_,
                color=Consts.PLOT_COLORS[idx],
            )

        # self.plot_particle_type(dataset=dataset,
        #     size_dataset_index=size_dataset_index,
        #     particle_type="Fraxinus",
        #     color="violet")

        # self.plot_particle_type(dataset=dataset,
        #                 size_dataset_index=size_dataset_index,
        #                 particle_type="Taxus",
        #                 color="peru")
        plt.xlabel("Diameter [μm]")
        plt.ylabel("Particles count")
        plt.legend(loc=(1.04, 0))
        plt_show(plt.gcf())

        logging.info(
            f"Average particles size used for training={round(np.average(renormalized_train_sizes))}µm"
        )
        logging.info(
            f"5th percentile size used for training={round(np.percentile(renormalized_train_sizes, 5), 2)}µm"
        )
        logging.info(
            f"25th percentile size used for training={round(np.percentile(renormalized_train_sizes, 25), 2)}µm"
        )
        logging.info(
            f"Median particles size used for training={round(np.mean(renormalized_train_sizes), 2)}µm"
        )
        logging.info(
            f"75th percentile size used for training={round(np.percentile(renormalized_train_sizes, 75), 2)}µm"
        )
        logging.info(
            f"95th percentile size used for training={round(np.percentile(renormalized_train_sizes, 95), 2)}µm"
        )

    def plot_particle_type(
        self,
        y_train: list[int],
        train_sizes: list[float],
        particle_type: str,
        color: str,
    ):
        typesConfig = Config.get(TypesConfig)
        particle_type_idx = typesConfig.pollen_types.index(particle_type)
        type_sizes = []
        for idx, train_size in enumerate(train_sizes):
            if y_train[idx] == particle_type_idx:
                type_sizes.append(train_size)
        renormalized_type_sizes = np.array(type_sizes) * 100
        plt.hist(
            renormalized_type_sizes,
            range=(0, 100),
            bins=100,
            histtype="bar",
            color=color,
            edgecolor="#169acf",
            linewidth=0.5,
            label=particle_type,
            alpha=0.5,
        )
        # plt.xticks(np.arange(0, 105, 5), rotation=45)
        # plt.xlim(0, 100)
