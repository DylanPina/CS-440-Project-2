from abc import ABC, abstractmethod
from typing import List
from config import Cell


class Bot(ABC):
    """Abstract base class for bots"""

    def __init__(self):
        pass

    def set_ship_layout(self, ship_layout: List[List[Cell]]) -> None:
        self.ship_layout = ship_layout

    @abstractmethod
    def setup(self) -> None:
        """Performs any initial setup which the bot needs to do"""

        pass

    @abstractmethod
    def move(self) -> List[int]:
        """Moves the bot to another cell in the ship and returns new position"""

        pass
