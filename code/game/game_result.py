from config import Bots
from typing import List


class GameResult:
    """Contains all the information regarding the result of a game"""

    def __init__(
        self,
        actions: int,
        bot_variant: Bots,
        ship_dimensions: List[int],
        run_time_ms: int,
    ):
        self.actions = actions
        self.bot_variant = bot_variant
        self.ship_dimensions = ship_dimensions
        self.run_time_ms = run_time_ms
