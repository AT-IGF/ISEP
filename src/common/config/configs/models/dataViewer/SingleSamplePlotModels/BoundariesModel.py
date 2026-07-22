from dataclasses import dataclass


@dataclass()
class BoundariesModel:
    exclude_lower_than: int | None = None
    exclude_higher_than: int | None = None
