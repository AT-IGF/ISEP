from dataclasses import dataclass


@dataclass
class KnnModel:
    train_knn: bool = False
    n_neighbors: int = 10
