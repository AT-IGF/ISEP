from dataclasses import dataclass


@dataclass
class UmapModel:
    """UMAP dimensionality reduction of the latent space before clustering, loaded from unsupervised training."""

    key: str = None
    """Internal identifier used by the UI."""

    path: str | None = None
    """Path to the UMAP model fitted during unsupervised training, relative to the resources directory.
    Pre-clustering step to reduce the dimensions of the autoencoder latent space."""

    pre_umap_normalization: str | None = "l2"
    """Normalization of the latent vectors before UMAP: ``l1``, ``l2``, ``max`` or ``None``. Has to be the
    same as ``pre_umap_normalization`` used during unsupervised training."""
