import logging
from abc import ABC
from typing import List, Optional, Tuple
from config import Cell
from collections import deque
from bots import Bot
from .sensory_data import SensoryData


class ProbabilisticBot(Bot, ABC):
    """Abstract base class for probabilistic bots"""

    def __init__(self, alpha: int):
        super().__init__()
        self.ship_layout = None
        self.D = None
        self.alpha = alpha
        self.starting_location = None
        self.bot_location = None
        self.sensory_data = List[SensoryData]
        self.traversal = []
        self.parent = {}
        self.open_cells = set()

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_matrix = [
            [SensoryData()] * self.D
            for _ in range(self.D)
        ]
        self.open_cell_count = self.D**2

        for row in range(self.D):
            for col in range(self.D):
                if (
                    self.ship_layout[row][col] == Cell.CLOSED
                ):
                    sensory_matrix[row][col].probability = 0
                    self.open_cells.add((row, col))

        return sensory_matrix

    def print_sensory_data(self) -> None:
        """Outputs the current sensory data to the log"""

        sensory_output = "\n--Sensory Data--\n"
        for row in range(len(self.sensory_data)):
            for col in range(len(self.sensory_data)):
                if (row, col) == self.bot_location:
                    sensory_output += f"X, "
                elif self.sensory_data[row][col].invalid:
                    sensory_output += "BRUH, "
                else:
                    sensory_output += f"{round(self.sensory_data[row][col].probability, 2)}, "

            sensory_output = sensory_output.rsplit(", ", 1)[0]
            if row != len(self.ship_layout) - 1:
                sensory_output += "\n"

        logging.debug(sensory_output)
