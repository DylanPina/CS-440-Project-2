import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from config import Cell, SensoryData
from collections import deque
from bots import Bot


class DeterministicBot(Bot):
    """Abstract base class for bots"""

    def __init__(self, k: int):
        super().__init__()
        self.ship_layout = None
        self.D = None
        self.k = k
        self.starting_location = None
        self.bot_location = None
        self.sensory_data = List[SensoryData]
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
    
    def closest_possible_leak_cell(
        self, target: SensoryData
    ) -> Optional[Tuple[List[List[int]]]]:
        """Returns the closest possible leak cell using BFS from bot's current location"""

        visited = set()
        queue = deque([self.bot_location])
        parent = {self.bot_location: self.bot_location}
        shortest_path = []

        while queue:
            row, col = queue.popleft()
            # Check the current cell
            if self.sensory_data[row][col] == target:
                shortest_path.append((row, col))

            # Mark the cell as visited
            visited.add((row, col))
            # Add the neighboring cells to the queue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                d_row, d_col = row + dr, col + dc
                if (
                    d_row in range(self.D)
                    and d_col in range(self.D)
                    and (d_row, d_col) not in visited
                    and (d_row, d_col) not in self.traversal
                    and self.ship_layout[d_row][d_col] != Cell.CLOSED
                    and self.sensory_data[d_row][d_col] != SensoryData.INVALID_CELL
                ):
                    queue.append((d_row, d_col))
                    parent[(d_row, d_col)] = (row, col)

        # If we found a reachable possible leak we reconstruct the path
        # which lead us there
        if shortest_path:
            while shortest_path[-1] != self.bot_location:
                r, c = parent[shortest_path[-1]]
                shortest_path.append((r, c))
            return (
                shortest_path[0],
                shortest_path[-2],
            )  # (closest possible leak cell, next step to get there)

        return None  # Return None if no cell is found

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

        logging.info(sensory_output)

    @abstractmethod
    def setup(self) -> None:
        """Performs any initial setup which the bot needs to do"""

        pass