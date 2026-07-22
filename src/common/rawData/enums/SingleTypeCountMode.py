from enum import Enum

class SingleTypeCountMode(Enum):
    STOP_ON_COUNT = 0
    """Taked only first number of samples given in 'single_type_count'"""
    RANDOM_FROM_ALL = 1
    """Takes all particles and then selectes randomly 'single_type_count'"""