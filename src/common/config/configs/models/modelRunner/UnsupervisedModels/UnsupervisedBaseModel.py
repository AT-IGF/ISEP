from dataclasses import dataclass


@dataclass
class UnsupervisedBaseModel:
    """Clusterer file and its cluster-to-pollen-type mapping."""

    run: bool = False

    path: str | None = None
    """Path to the clusterer file saved during unsupervised training, relative to the resources directory."""

    mapping_path: str | None = None
    """Clusters mapping path. JSON file mapping every pollen type to the list of clusters it belongs to,
    e.g. ``{"Alnus": [1, 2, 4], "Corylus": [3]}``. Keys have to be pollen type names from ``pollen_types``,
    and one cluster can be assigned to more than one pollen type. Predictions of pollen types missing from
    the mapping are removed."""

    key: str = None  # ui purposes
    """Internal identifier used by the UI."""
