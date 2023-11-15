import logging
import argparse
from enum import Enum
from typing import List
from collections import namedtuple

# Output file for ship layout
INITIAL_SHIP_LAYOUT_OUTPUT_FILE = "output/initial_ship_layout.log"
# Output file for the traversal
SHIP_LAYOUT_TRAVERSAL_OUTPUT_FILE = "output/ship_layout_traversal.log"


class Cell(Enum):
    """Enum type for a ship layout cell"""

    CLOSED = 0
    OPEN = 1
    BOT = 2
    LEAK = 3

    def __str__(self):
        return "%s" % self.value


class Bots(Enum):
    """Enum type for bots"""

    BOT1 = 1
    BOT2 = 2
    BOT3 = 3
    BOT4 = 4
    BOT5 = 5
    BOT6 = 6
    BOT7 = 7
    BOT8 = 8
    BOT9 = 9

    def __str__(self):
        return f"Bot {self.value}"


class GameResult:
    """Contains all the information regarding the result of a game"""

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


Quadrant = namedtuple("Quadrant", "name cells")


def init_logging() -> None:
    """Initializes logging capabilities for entire applicaiton"""

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
    log_level = log_levels[args.log_level] if args.log_level else logging.ERROR
    logging.basicConfig(level=log_level, filename="logs/log.log",
                        filemode="w", format='%(asctime)s - [%(levelname)s]: %(message)s')
