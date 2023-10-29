from enum import Enum
from typing import List


class Cell(Enum):
    CLOSED = 0
    OPEN = 1
    BOT = 2

    def __str__(self):
        return '%s' % self.value


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


class GameResult():
    def __init__(self, outcome: bool, bot_variant: Bots, ship_dimensions: List[int], q: int, run_time_ms: int):
        self.outcome = outcome
        self.bot_variant = bot_variant
        self.ship_dimensions = ship_dimensions
        self.q = q
        self.run_time_ms = run_time_ms

    def __str__(self):
        return f"\n[Outcome]: {'Success' if self.outcome else 'Failure'}\
                \n[Bot]: {self.bot_variant}\
                \n[Ship Dimensions]: {self.ship_dimensions}\
                \n[Fire Spread Probability]: {100 * self.q}%\
                \n[Run Time]: {self.run_time_ms}ms\n"


SHIP_LAYOUT_OUTPUT = "output/ship_layout.csv"
