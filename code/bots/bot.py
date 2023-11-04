from abc import ABC, abstractmethod
from typing import List


class Bot(ABC):
    """Abstract base class for bots"""

    def __init__(self):
        self.ship_layout = None
        self.D = None
        self.starting_location = None
        self.bot_location = None
        self.visited = set()
        self.traversal = []
        self.parent = {}

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
