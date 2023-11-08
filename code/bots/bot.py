from abc import ABC, abstractmethod
from typing import List
from config import Cell


class Bot(ABC):
    """Abstract base class for bots"""

    def __init__(self):
        self.ship_layout = None
        self.D = None
        self.starting_location = None
        self.bot_location = None
        self.leak_location = None
        self.visited = set()
        self.traversal = []
        self.parent = {}

    def set_ship_layout(self, ship_layout: List[List[Cell]]) -> None:
        """Passes the ship layout to the bot"""

        self.ship_layout = ship_layout
        self.D = len(ship_layout)

    def get_traversal(self) -> List[List[int]]:
        """Returns a matrix representing the bot's final traversal path"""

        if not self.traversal:
            return []

        traversal_matrix = [
            [Cell.CLOSED] * len(self.ship_layout) for _ in range(len(self.ship_layout))
        ]

        for r, c in self.traversal[:-1]:
            traversal_matrix[r][c] = Cell.OPEN

        r, c = self.traversal[-1]
        traversal_matrix[r][c] = self.ship_layout[r][c]
        return traversal_matrix

    @abstractmethod
    def setup(self) -> None:
        """Performs any initial setup which the bot needs to do"""

        pass

    @abstractmethod
    def initialize_sensory_data(self) -> List[List[any]]:
        """Returns a matrix representing the bot's initial sensory data"""

        pass

    @abstractmethod
    def action(self, timestep: int) -> None:
        """Performs the bot's next action"""

        pass

    @abstractmethod
    def next_step(self) -> List[int]:
        """Finds the 'best' next step to make from bot's current location and returns that step"""

        pass

    @abstractmethod
    def move(self) -> List[int]:
        """Moves the bot to another cell in the ship and returns new position"""

        pass

    @abstractmethod
    def sense(self) -> None:
        """Updates sensory data about the environment"""

        pass

    @abstractmethod
    def print_stats(self, timesteps: int) -> None:
        """Prints the bots final stats after it has found the leak"""

        pass
