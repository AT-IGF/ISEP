from dataclasses import dataclass


@dataclass()
class PlotsModel:
    spectrum_max_y: int | None = 15000
    lifetime_max_y: int | None = 4000