import logging
from matplotlib import pyplot as plt
import numpy as np

from src.modelBuilder.dataInspectors.UmapInspetor import plot_embeddings


def plot_pca(latent_vectors, color_label_map, labels):
    plot_embeddings(
        embeddings=latent_vectors,
        components_count=latent_vectors.shape[1],
        color_label_map=color_label_map,
        labels=labels,
        path="",
    )
