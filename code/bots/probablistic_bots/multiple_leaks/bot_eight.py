import logging
import random
import copy
from .probabilistic_bot_multiple_leaks import ProbabilisticBotMultipleLeaks
from typing import Tuple, List
from config import Bots, Cell
from math import e
from ..sensory_data import SensoryData
from collections import defaultdict, deque


class BotEight(ProbabilisticBotMultipleLeaks):
    """
    Bot 8 is exactly Bot 3, except that the probability updates must be corrected to account for the fact that there are two leaks.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT8

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")
