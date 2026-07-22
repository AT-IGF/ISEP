from typing import Iterable

import numpy as np

def get_set_by_feature(dataset = Iterable[list[list[float]]]):
    return [np.array(feature) for feature in  list(zip(*dataset))]

