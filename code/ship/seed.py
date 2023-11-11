import logging
import csv
from config import Cell
from typing import List


class Seed():
    def __init__(self, file: str, multi_leaks: bool = False):
        self.layout = self.read_ship_layout_from_file(file)
        self.D = len(self.layout)
        self.closed_cells = set()
        self.open_cells = set()
        self.bot_location = None
        self.multi_leaks = multi_leaks

        if self.multi_leaks:
            self.leak_locations = []
        else:
            self.leak_location = None

        self.get_cells()
        logging.info(f"Ship dimensions: {self.D} x {self.D}")
        logging.info(f"Seed type: singular leak")

    def read_ship_layout_from_file(self, file: str) -> List[List[Cell]]:
        """
        Reads the string representation of a ship layout from the file location given by
        'file' and returns a functional ship layout.
        """

        logging.info(f"Using seed: {file}")
        layout = []
        reader = csv.reader(open(file))
        for row in reader:
            vals = [i.strip() for i in row]
            enums = []
            for val in vals:
                if val == str(Cell.CLOSED.value):
                    enums.append(Cell.CLOSED)
                elif val == str(Cell.OPEN.value):
                    enums.append(Cell.OPEN)
                elif val == str(Cell.BOT.value):
                    enums.append(Cell.BOT)
                elif val == str(Cell.LEAK.value):
                    enums.append(Cell.LEAK)
            layout.append(enums)
        return layout

    def get_cells(self) -> None:
        """Populates the cells in the seed ship layout with their respective Cell types"""

        if self.multi_leaks:
            for r in range(self.D):
                for c in range(self.D):
                    if self.layout[r][c] == Cell.CLOSED:
                        self.closed_cells.add((r, c))
                    elif self.layout[r][c] == Cell.OPEN:
                        self.open_cells.add((r, c))
                    elif self.layout[r][c] == Cell.BOT:
                        self.bot_location = (r, c)
                    elif self.layout[r][c] == Cell.LEAK:
                        self.leak_locations.append((r, c))
        else:
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
