import logging
from abc import abstractmethod, ABC
from config import read_ship_layout_from_file


class Seed(ABC):
    def __init__(self, file: str):
        self.layout = read_ship_layout_from_file(file)
        self.D = len(self.layout)
        self.closed_cells = set()
        self.open_cells = set()
        self.bot_location = None
        self.leak_location = None
        self.get_cells()
        logging.info(f"Ship dimensions: {self.D} x {self.D}")
        logging.info(f"Seed type: singular leak")

    @abstractmethod
    def get_cells(self) -> None:
        """Parses the ship layout and populates global variables"""

        pass
