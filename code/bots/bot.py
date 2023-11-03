from abc import ABC, abstractmethod
from typing import List
from config import Cell, SensoryData


class Bot(ABC):
    """Abstract base class for bots"""

    def __init__(self, k: int):
        self.ship_layout = None
        self.k = k
        self.D = None
        self.starting_location = None
        self.bot_location = None
        self.visited = set()
        self.traversal = []
        self.parent = {}

    def set_ship_layout(self, ship_layout: List[List[Cell]]) -> None:
        self.ship_layout = ship_layout
        self.D = len(ship_layout)

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_matrix = [
            [SensoryData.NO_LEAK] * len(self.ship_layout)
            for _ in range(len(self.ship_layout))
        ]

        for row in range(len(self.ship_layout)):
            for col in range(len(self.ship_layout)):
                if (
                    self.ship_layout[row][col] == Cell.OPEN
                    or self.ship_layout[row][col] == Cell.LEAK
                ):
                    sensory_matrix[row][col] = SensoryData.POSSIBLE_LEAK

        return sensory_matrix

    def get_traversal(self) -> List[List[int]]:
        """Returns a matrix representing the traversal"""

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

    def print_sensory_data(self) -> None:
        """Prints the current sensory data to the console"""

        sensory_output = "--Sensory Data--\n"
        for row in range(len(self.sensory_data)):
            for col in range(len(self.sensory_data)):
                if (row, col) == self.bot_location:
                    sensory_output += f"X, "
                    continue
                sensory_output += f"{self.sensory_data[row][col].value}, "

            sensory_output = sensory_output.rsplit(", ", 1)[0]
            if row != len(self.ship_layout) - 1:
                sensory_output += "\n"

        print(sensory_output)

    @abstractmethod
    def setup(self) -> None:
        """Performs any initial setup which the bot needs to do"""

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
