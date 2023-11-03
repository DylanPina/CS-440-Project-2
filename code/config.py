from enum import Enum
from typing import List
from dataclasses import dataclass


class Cell(Enum):
    CLOSED = 0
    OPEN = 1
    BOT = 2
    LEAK = 3

    def __str__(self):
        return "%s" % self.value


class SensoryData(Enum):
    NO_LEAK = 0
    POSSIBLE_LEAK = 1
    INVALID_CELL = 2
    IN_PROXIMITY = 3
    LEAK = 4


class Bots(Enum):
    BOT1 = 1
    BOT2 = 2
    BOT3 = 3
    BOT4 = 4
    BOT5 = 5
    BOT6 = 6
    BOT7 = 7
    BOT8 = 8

    def __str__(self):
        return f"Bot {self.value}"


class GameResult:
    def __init__(
        self,
        outcome: bool,
        bot_variant: Bots,
        ship_dimensions: List[int],
        run_time_ms: int,
    ):
        self.outcome = outcome
        self.bot_variant = bot_variant
        self.ship_dimensions = ship_dimensions
        self.run_time_ms = run_time_ms


SHIP_LAYOUT_OUTPUT = "output/ship_layout.csv"
