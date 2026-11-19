from dataclasses import dataclass


@dataclass()
class BoundariesModel:
    """Range of the aggregated signal value within which a single particle is plotted. The value is the
    maximum for lifetime and spectrum, and the average for scattering."""

    exclude_lower_than: int | None = None
    """Exclude, if the aggregated value is below. Display only samples whose aggregated value is equal to
    or above the threshold, in arbitrary units (AU). ``None`` disables the lower boundary."""

    exclude_higher_than: int | None = None
    """Exclude, if the aggregated value is above. Display only samples whose aggregated value is equal to
    or below the threshold, in arbitrary units (AU). ``None`` disables the upper boundary."""
