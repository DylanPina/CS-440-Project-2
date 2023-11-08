import logging
from config import Cell, read_ship_layout_from_file


class SingleSeed:
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
                    self.leak_location = (r, c)
