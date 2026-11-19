from dataclasses import dataclass


@dataclass()
class LearningRateReducerModel:
    """Learning rate reduction on plateau."""

    enabled: bool
    """Is learning rate reducer enabled. Allows to decrease the learning rate when training stops
    progressing. The validation accuracy is monitored in supervised training and the validation loss
    in unsupervised training."""

    patience: int
    """Patience. How many epochs to wait to decrease the learning rate by factor, when min delta progress
    is not obtained."""

    min_lr: float
    """Min learning rate. Lower bound below which the learning rate will not be decreased."""

    min_delta: float
    """Min delta. Minimal progress below which patience epochs are counted. E.g. if min delta equals 0.2
    and the monitored metric improves by less than that value for patience epochs, the learning rate will
    be decreased by decrease factor."""

    factor: float
    """Decrease factor. Multiplier by which the learning rate is decreased when patience is exceeded."""
