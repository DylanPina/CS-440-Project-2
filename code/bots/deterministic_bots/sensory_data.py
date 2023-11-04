from enum import Enum


class SensoryData(Enum):
    NO_LEAK = 0
    POSSIBLE_LEAK = 1
    INVALID_CELL = 2
    LEAK = 3
    IN_PROXIMITY = 4
