from dataclasses import dataclass


@dataclass
class PcaModel:
    key: str = None
    components: int | float = 0
