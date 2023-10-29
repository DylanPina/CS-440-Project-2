import csv
from config import Cell
from typing import List


class Seed:
    def __init__(self, file: str):
        self.layout = self.read_from_file(file)
        self.D = len(self.layout)
        self.closed_cells = set()
        self.open_cells = set()
        self.bot_location = None
        self.leak_location = None
        self.get_cells()

    def read_from_file(self, file: str) -> List[int]:
        """
        Reads the string representation of a ship layout from the file location given by 
        'file' and returns a functional ship layout.
        """

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
        """Parses the ship layout and populates global variables"""

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
