import logging
import numpy as np

from collections import Counter
from src.modelBuilder.summaries.PrecRecallSummary import PrecRecallSummary
from src.common.predictions.Thresholds import is_any_pred_within_threshold

from src.modelBuilder.confusionMatrix import make_confusion_matrix
from src.modelBuilder.datasetHandler.models import DatasetSplitModel
from src.modelBuilder.summaries.models import SummaryDataFrameModel
from sklearn.metrics import f1_score, precision_score, recall_score

LOSS_INDEX = 0
ACCURACY_INDEX = 1


def calculate_thresholds(
    y_pred,
    dataset: DatasetSplitModel,
    model,
    thresholds: list[float],
    pollen_types: list,
):
    if thresholds == []:
        logging.getLogger().info(
            "Threshold summary 'thresholds' property is an empty list. Add values between 0-1 to calcualte predicions within thresholds"
        )
        return

    pred_summaries: list[SummaryDataFrameModel] = []
    for threshold in thresholds:
        logging.getLogger().info(f"Evaluation with threshold={threshold}")
        y_pred_threshold = []
        y_test_threshold = []
        X_test_threshold = {}
        for i in range(0, len(y_pred)):
            if is_any_pred_within_threshold(y_pred=y_pred[i], threshold=threshold):
                y_pred_threshold.append(y_pred[i])
                y_test_threshold.append(dataset.y_test[i])
                for key, value in dataset.X_test.items():
                    X_test_threshold.setdefault(key, []).append(value[i])

        for key, value in X_test_threshold.items():
            X_test_threshold[key] = np.array(value)

        if len(y_pred_threshold) == 0:
            logging.getLogger().warn(
                f"Threshold={threshold} value is to high. No samples found, count={len(y_pred_threshold)}"
            )
            continue

        metrics = model.evaluate(X_test_threshold, np.array(y_test_threshold))
        pred_summary = sorted(
            Counter(np.array(y_pred_threshold).argmax(axis=1)).items()
        )
        y_test_threshold_max = np.array(y_test_threshold).argmax(axis=-1)
        y_pred_threshold_max = np.array(y_pred_threshold).argmax(axis=-1)
        prec = precision_score(
            y_test_threshold_max, y_pred_threshold_max, average="macro"
        )
        recall = recall_score(
            y_test_threshold_max, y_pred_threshold_max, average="macro"
        )
        pred_summaries.append(
            SummaryDataFrameModel(
                threshold=threshold,
                loss=round(metrics[LOSS_INDEX], 2),
                accuracy=round(metrics[ACCURACY_INDEX], 2),
                precission=prec,
                recall=recall,
                f1=PrecRecallSummary.calculate_f1(prec=prec, recall=recall),
                pollen_types=pollen_types,
                pred_summary=dict(pred_summary),
                no_threshold_count=len(y_pred),
                threshold_count=len(y_pred_threshold),
            )
        )

    show_as_data_frame(summaries=np.array(pred_summaries))

    if len(thresholds) == 1 and pollen_types is not None:

        make_confusion_matrix(
            y_pred=np.array(y_pred_threshold).argmax(axis=1),
            y_true=np.array(y_test_threshold).argmax(axis=1),
            classes=pollen_types,
            summary=f"Threshold={thresholds[0]}",
        )


def show_as_data_frame(summaries: list[SummaryDataFrameModel]):
    import pandas as pd

    data = {
        "threshold": [x.threshold for x in summaries],
        "loss": [x.loss for x in summaries],
        "accuracy": [x.accuracy for x in summaries],
        "precission": [x.precission for x in summaries],
        "recall": [x.recall for x in summaries],
        "f1": [x.f1 for x in summaries],
        "no_threshold_count": [x.no_threshold_count for x in summaries],
        "threshold_count": [x.threshold_count for x in summaries],
    }

    for summary in summaries:
        keys = summary.pred_summary.keys()
        for idx, pollen_type in enumerate(summary.pollen_types):
            if f"type_{idx}" not in data.keys():
                data[f"type_{idx}"] = []

            if idx in keys:
                data[f"type_{idx}"].append(summary.pred_summary[idx])
            else:
                data[f"type_{idx}"].append(0)

    logging.getLogger().info(f"\n{pd.DataFrame(data).to_string()}")
