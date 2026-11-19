from dataclasses import dataclass


@dataclass()
class EarlyStoppingModel:
    """Early stopping of training."""

    enabled: bool
    """Is early stopping enabled. Allows to stop model training earlier based on conditions. The
    validation loss is monitored, and the weights of the best epoch are restored."""

    min_delta: float
    """Min delta. Minimal decrease of the validation loss counted as progress."""

    patience: int
    """Patience. How many epochs to wait till training will be stopped, when min delta progress is not
    obtained."""
