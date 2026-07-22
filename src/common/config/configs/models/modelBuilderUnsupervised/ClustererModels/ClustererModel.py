from dataclasses import dataclass, field


@dataclass
class ClustererModel:

    run_clusterer: bool = False
    cluster_sizes: list[int] = field(default_factory=lambda: [20, 30, 40])
    cluster_percentiles: list[float] | None = field(
        default_factory=lambda: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    )
