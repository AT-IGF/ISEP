import logging
import itertools
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix

from src.core.plots.plotting_utils import plt_show


def plot_confucion_matrix(cm, summary, classes, y_true, y_pred):
    cm_norm = (
        cm.astype("float") / np.abs(cm).sum(axis=1)[:, np.newaxis]
    )  # normalize our confusion matrix
    n_classes = cm.shape[0]

    # Prittify
    fig, ax = plt.subplots(figsize=(15, 15))
    cax = ax.matshow(cm, cmap=plt.colormaps["Blues"])
    fig.colorbar(cax)

    # Create classes
    if classes:
        combined = np.concatenate((y_true, y_pred), axis=0)
        y_true_set = set(combined)
        labels = []
        for index, label in enumerate(classes):
            if index in y_true_set:
                labels.append(label)
        n_classes = len(labels)
    else:
        labels = np.arange(cm.shape[0])

        # label the axis
    ax.set(
        title=f"Confusion matrix {summary}",
        xlabel="Predicted label",
        ylabel="True label",
        xticks=np.arange(n_classes),
        yticks=np.arange(n_classes),
        xticklabels=labels,
        yticklabels=labels,
    )

    ax.xaxis.set_label_position("bottom")
    ax.xaxis.tick_bottom()
    plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment="right")

    ax.xaxis.label.set_size(24)
    ax.yaxis.label.set_size(24)

    # Threshold for different colors
    threshold = (cm.max() + cm.min()) / 2

    # Plot text on each cell
    text_size = 12
    if len(labels) < 5:
        text_size = 16
    elif len(labels) < 8:
        text_size = 14
    elif text_size > 20:
        text_size = 10
        
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(
            j,
            i,
            f"{cm[i, j]}\n({cm_norm[i, j] * 100:.1f}%)",
            horizontalalignment="center",
            color="white" if cm[i, j] > threshold else "black",
            size=text_size,
        )
    if summary != "test":
        plt_show(plt.gcf())


def make_confusion_matrix(
    y_true, y_pred, summary: str, classes: Optional[list[str]] = None, y_pred_diff=None
):
    logging.getLogger().info("Plotting confusion matrix")
    cm = confusion_matrix(y_true=y_true, y_pred=y_pred)
    plot_confucion_matrix(
        cm=cm,
        summary=f"{summary} - trained model",
        classes=classes,
        y_true=y_true,
        y_pred=y_pred,
    )
    if y_pred_diff is not None:
        import seaborn as sns

        cm2 = confusion_matrix(y_true=y_true, y_pred=y_pred_diff)
        plot_confucion_matrix(
            cm=cm2,
            summary=f"{summary} - another model",
            classes=classes,
            y_true=y_true,
            y_pred=y_pred,
        )
        cm_diff = cm - cm2
        plot_confucion_matrix(
            cm=cm_diff,
            summary=f"{summary} - difference (trained - another)",
            classes=classes,
            y_true=y_true,
            y_pred=y_pred,
        )
