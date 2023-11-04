import logging, argparse
from enum import Enum
from typing import List


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
    LEAK = 3
    IN_PROXIMITY = 4


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


def init_logging() -> None:
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level')
    args = parser.parse_args()
    log_level = log_levels[args.log_level]

    logging.basicConfig(level=log_level, filename="logs/log.log", filemode="w", format='%(asctime)s - [%(levelname)s]: %(message)s')

SHIP_LAYOUT_OUTPUT = "output/ship_layout.csv"
