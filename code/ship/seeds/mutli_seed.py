import logging
from config import Cell, read_ship_layout_from_file
from .seed import Seed


class MultiSeed(Seed):
    """Ship layout seed with multiple leaks"""

    def __init__(self, file: str):
        self.layout = read_ship_layout_from_file(file)
        self.D = len(self.layout)
        self.closed_cells = set()
        self.open_cells = set()
        self.bot_location = None
        self.leak_locations = set()
        self.get_cells()
        logging.info(f"Ship dimensions: {self.D} x {self.D}")
        logging.info(f"Seed type: multiple leaks")

    def get_cells(self) -> None:
        for r in range(self.D):
            for c in range(self.D):
                if self.layout[r][c] == Cell.CLOSED:
                    self.closed_cells.add((r, c))
                elif self.layout[r][c] == Cell.OPEN:
                    self.open_cells.add((r, c))
                elif self.layout[r][c] == Cell.BOT:
                    self.bot_location = (r, c)
                elif self.layout[r][c] == Cell.LEAK:
                    self.leak_locations.add((r, c))
