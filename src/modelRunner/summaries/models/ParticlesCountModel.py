from dataclasses import dataclass


@dataclass
class ParticlesCountModel:
    with_threshold_count: int
    no_threshold_count: int
    total_count: int