import logging
import numpy as np

from collections import Counter
from src.core.plots.plotting_utils import plt_show
from src.common.config import Config, TypesConfig
from src.common.predictions.Thresholds import is_any_pred_within_threshold

from src.modelBuilder.confusionMatrix import make_confusion_matrix
from src.modelBuilder.datasetHandler.models import DatasetSplitModel
from src.modelBuilder.summaries.models import SummaryDataFrameModel

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, precision_score, recall_score
import tensorflow as tf
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import (
    roc_curve,
    auc,
    roc_auc_score,
    precision_recall_curve,
    confusion_matrix,
)
from src.common import Consts

plt.rcParams.update({"font.size": 16})


class ROCSummary:

    def __init__(self) -> None:
        self._logger = logging.getLogger()
        self.typesConfig = Config.get(TypesConfig)

    def summary(self, y_pred, dataset: DatasetSplitModel):
        self.multiclass_roc_auc_score(dataset.y_test, y_pred)

    def print_roc_summary(self, y_pred, y_test, origin_score: float | None = None):
        score = roc_auc_score(y_true=y_test, y_score=y_pred, multi_class="ovr")
        diff_score = ""
        if origin_score != None:
            diff_score = f", diff={(origin_score - score)*100:.2f}%"
        self._logger.info(f"ROC AUC score: {score*100:.2f}%" + diff_score)
        return score

    def plot_roc_curve(self, tpr, fpr, label, color, scatter=True):
        if scatter:
            plt.scatter(x=fpr, y=tpr)
        plt.plot(fpr, tpr, label=label, color=color, linewidth=0.7)
        plt.plot([0, 1], [0, 1])

    def calculate_tpr_fpr(self, y_real, y_pred):
        # Calculates the confusion matrix and recover each element
        cm = confusion_matrix(y_real, y_pred)
        TN = cm[0, 0]
        FP = cm[0, 1]
        FN = cm[1, 0]
        TP = cm[1, 1]
        # Calculates tpr and fpr
        tpr = TP / (TP + FN)  # sensitivity - true positive rate
        fpr = 1 - TN / (TN + FP)  # 1-specificity - false positive rate

        return tpr, fpr

    def get_n_roc_coordinates(self, y_real, y_proba, resolution=50):
        tpr_list = [0]
        fpr_list = [0]
        for i in range(resolution):
            threshold = i / resolution
            y_pred = y_proba > threshold
            tpr, fpr = self.calculate_tpr_fpr(y_real, y_pred)
            tpr_list.append(tpr)
            fpr_list.append(fpr)
        return tpr_list, fpr_list

    def multiclass_roc_auc_score(self, y_test, y_pred):
        plt.figure(figsize=(12, 8))

        lb = LabelBinarizer()
        lb.fit(y_test)
        y_test = lb.transform(y_test)
        # y_pred = lb.transform(y_pred)

        tpr_s, fpr_s = [], []
        for idx, c_label in enumerate(self.typesConfig.pollen_types):

            tpr, fpr = self.get_n_roc_coordinates(
                y_test[:, idx], y_pred[:, idx], resolution=100
            )
            tpr_s.append(tpr)
            fpr_s.append(fpr)
            self.plot_roc_curve(
                tpr, fpr, c_label, Consts.PLOT_COLORS[idx], scatter=False
            )

        tpe_s_mean = np.mean(tpr_s, axis=0)
        fpr_s_mean = np.mean(fpr_s, axis=0)

        tpe_s_std = np.std(tpr_s, axis=0)
        fpr_s_std = np.std(fpr_s, axis=0)

        plt.fill_between(
            fpr_s_mean,
            tpe_s_mean - tpe_s_std,
            tpe_s_mean + tpe_s_std,
            color="indigo",
            alpha=0.5,
        )
        plt.plot([0, 1], [0, 1], color="green")

        plt.xlim(-0.05, 1.05)
        plt.ylim(-0.05, 1.05)
        plt.xlabel("1 - specificity")
        plt.ylabel("recall")
        plt.legend(loc=(1.04, 0))
        plt.grid()
        plt_show(plt.gcf())
        # plt.close()

    # https://towardsdatascience.com/interpreting-roc-curve-and-roc-auc-for-classification-evaluation-28ec3983f077
