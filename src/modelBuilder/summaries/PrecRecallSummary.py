import json
import logging
import numpy as np


import pandas as pd
from src.core.plots.plotting_utils import plt_show
from src.common.config import Config, TypesConfig

from src.modelBuilder.datasetHandler.models import DatasetSplitModel

import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import (
    confusion_matrix,
)
from src.common import Consts


class PrecRecallSummary:
    F1_MODE = "F1"
    PREC_RECALL_MODE = "PREC_RECALL"
    MODES = [F1_MODE, PREC_RECALL_MODE]

    def __init__(self) -> None:
        self._logger = logging.getLogger()
        self.typesConfig = Config.get(TypesConfig)

    def summary(self, y_pred, dataset: DatasetSplitModel, mode):
        self.multiclass_roc_auc_score(dataset.y_test, y_pred, mode)

    @staticmethod
    def calculate_f1(prec, recall):
        return 2 * (prec * recall) / (prec + recall)

    def print_prec_recall_summary(
        self, y_pred, dataset, origin_prec_recall: list | None = None
    ):
        prec = precision_score(dataset.y_test_max, np.array(y_pred), average="macro")
        recall = recall_score(dataset.y_test_max, np.array(y_pred), average="macro")
        f1 = self.calculate_f1(prec=prec, recall=recall)

        prec_diff = ""
        recall_diff = ""
        f1_diff = ""
        if origin_prec_recall is not None:
            diff_prec = origin_prec_recall[0]
            diff_recall = origin_prec_recall[1]
            diff_f1 = self.calculate_f1(diff_prec, diff_recall)
            prec_diff = f", diff={(diff_prec - prec)*100:.2f}%"
            recall_diff = f", diff={(diff_recall - recall)*100:.2f}%"
            f1_diff = f", diff={(diff_f1 - f1)*100:.2f}%"
        self._logger.info(f"Precission: {prec*100:.2f}%" + prec_diff)
        self._logger.info(f"Recall: {recall*100:.2f}%" + recall_diff)
        self._logger.info(f"F1: {f1*100:.2f}%" + f1_diff)

        return [prec, recall]

    def plot_prec_recall_curve(self, fpr, tpr, label, idx, scatter=True):
        if scatter:
            plt.plot(
                fpr,
                tpr,
                color=Consts.PLOT_COLORS[idx],
                label=label,
                marker=Consts.PLOT_MARKERS[idx],
                linewidth=1,
                markevery=15,
            )
        else:
            plt.plot(fpr, tpr, color=Consts.PLOT_COLORS[idx], label=None, linewidth=1.5)
            plt.plot(
                [],
                [],
                label=label,
                color=Consts.PLOT_COLORS[idx],
                marker=Consts.PLOT_MARKERS[idx],
                linewidth=1,
            )
        # plt.plot([0, 1], [0, 1])

    def calculate_recall_precission(self, y_real, y_pred):
        # Calculates the confusion matrix and recover each element
        cm = confusion_matrix(y_real, y_pred)
        TN = cm[0, 0]
        FP = cm[0, 1]
        FN = cm[1, 0]
        TP = cm[1, 1]
        # Calculates tpr and fpr
        recall = TP / (TP + FN)  # sensitivity - true positive rate
        precission = TP / (TP + FP)  # 1-specificity - false positive rate

        return recall, precission

    def get_n_prec_recall_coordinates(self, y_real, y_proba, resolution=50):
        recall_list = []
        precission_list = []
        threshold_list = []
        for i in range(resolution):
            threshold = i / resolution
            y_pred = y_proba > threshold
            recall, precission = self.calculate_recall_precission(y_real, y_pred)
            recall_list.append(recall)
            precission_list.append(precission)
            threshold_list.append(threshold)
        return (
            np.array(recall_list),
            np.array(precission_list),
            np.array(threshold_list),
        )

    def plot_cross_point(self, threshols, precision, recall, cls_idx, mode):
        if mode == self.F1_MODE:
            f1 = self.calculate_f1(precision, recall)
            best_idx = np.nanargmax(f1)

            plt.scatter(
                threshols[best_idx],
                f1[best_idx],
                s=200,
                c=Consts.PLOT_COLORS[cls_idx],
                marker=Consts.PLOT_MARKERS[cls_idx],
                alpha=1,
            )
            return best_idx
        else:
            diff = precision - recall
            idxs = np.where(diff[:-1] * diff[1:] < 0)[0]
            if len(idxs) == 0:
                logging.getLogger().warn(
                    f"No crossing found between precision and recall. Skipped. Idx={cls_idx}"
                )
                return
            idx = idxs[0]
            t = diff[idx] / (diff[idx] - diff[idx + 1])
            thr_cross = threshols[idx] + t * (threshols[idx + 1] - threshols[idx])
            score_cross = precision[idx] + t * (precision[idx + 1] - precision[idx])

            plt.scatter(
                thr_cross,
                score_cross,
                s=200,
                c=Consts.PLOT_COLORS[cls_idx],
                marker=Consts.PLOT_MARKERS[cls_idx],
                alpha=1,
            )
            return idx

    def multiclass_roc_auc_score(self, y_test, y_pred, mode):
        if mode not in self.MODES:
            raise ValueError(
                f"Mode not found, mode='{mode}', allowed modes=[{' '.join(self.MODES)}]"
            )

        plt.figure(figsize=(12, 8))
        plt.rcParams.update({"font.size": 24})

        lb = LabelBinarizer()
        lb.fit(y_test)
        y_test = lb.transform(y_test)
        # y_pred = lb.transform(y_pred)

        recalls, precissions, f1s, thresholds = [], [], [], []
        df = pd.DataFrame()
        for idx, c_label in enumerate(self.typesConfig.pollen_types):
            # fpr, tpr, thresholds = roc_curve(y_test[:,idx].astype(int), y_pred[:,idx])
            # self._c_ax.plot(fpr, tpr, label = '%s (AUC:%0.2f)'  % (c_label, auc(fpr, tpr)))

            recall_list, precission_list, threshold_list = (
                self.get_n_prec_recall_coordinates(
                    y_test[:, idx], y_pred[:, idx], resolution=100
                )
            )
            f1 = self.calculate_f1(precission_list, recall_list)
            recalls.append(recall_list)
            precissions.append(precission_list)
            f1s.append(f1)
            thresholds = threshold_list
            if mode == self.F1_MODE:
                self.plot_prec_recall_curve(
                    threshold_list, f1, c_label, idx, scatter=False
                )
                best_idx = self.plot_cross_point(
                    threshold_list, recall_list, precission_list, idx, mode
                )
                df_row = pd.DataFrame(
                    {
                        "label": [c_label],
                        "f1": [f1[best_idx]],
                        "threshold": [thresholds[best_idx]],
                    }
                )
                df = pd.concat([df, df_row], ignore_index=True)
            elif mode == self.PREC_RECALL_MODE:
                self.plot_prec_recall_curve(
                    threshold_list, recall_list, None, idx, scatter=False
                )
                self.plot_prec_recall_curve(
                    threshold_list, precission_list, c_label, idx, scatter=False
                )
                best_idx = self.plot_cross_point(
                    threshold_list, recall_list, precission_list, idx, mode
                )
                df_row = pd.DataFrame(
                    {
                        "label": [c_label],
                        "prec-recall": [f1[best_idx]],
                        "threshold": [thresholds[best_idx]],
                    }
                )
                df = pd.concat([df, df_row], ignore_index=True)
            else:
                return
        self._logger.info("\n%s", df)
        self._logger.info(
            f"Threshold mapping: {json.dumps(df.set_index('label')['threshold'].to_dict())}"
        )
        if mode == self.F1_MODE:
            f1s_mean = np.mean(f1s, axis=0)
            plt.plot(
                thresholds,
                f1s_mean,
                label="Average",
                linewidth=3,
                color="blue",
                linestyle="--",
            )
        elif mode == self.PREC_RECALL_MODE:
            recalls_mean = np.mean(recalls, axis=0)
            precissions_mean = np.mean(precissions, axis=0)

            recalls_std = np.std(recalls, axis=0)
            precissions_std = np.std(precissions, axis=0)
            plt.fill_between(
                thresholds,
                recalls_mean - recalls_std,
                recalls_mean + recalls_std,
                color="indigo",
                alpha=0.1,
                label="Recall",
                zorder=-1,
            )
            plt.fill_between(
                thresholds,
                precissions_mean + precissions_std,
                precissions_mean - precissions_std,
                color="cyan",
                alpha=0.1,
                label="Precission",
                zorder=-1,
            )
            plt.plot(
                thresholds, precissions_mean, label="Average", linewidth=2, color="blue"
            )
            plt.plot(thresholds, recalls_mean, label="", linewidth=2, color="blue")
        else:
            return

        # plt.plot([0, 1], [0, 1], color = 'green')

        plt.xlim(-0.05, 1.05)
        plt.ylim(-0.05, 1.05)
        plt.xlabel("Threshold")
        plt.ylabel("Precission / Recall")
        plt.legend(
            loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=5, markerscale=2.5
        )
        plt.subplots_adjust(bottom=0.25, top=0.98)
        plt.grid()
        plt_show(plt.gcf())
        plt.close()

    # https://towardsdatascience.com/interpreting-roc-curve-and-roc-auc-for-classification-evaluation-28ec3983f077
