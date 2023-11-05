import logging
from abc import ABC
from typing import List, Optional, Tuple
from config import Cell
from collections import deque
from bots import Bot
from .sensory_data import SensoryData


class ProbabilisticBot(Bot, ABC):
    """Abstract base class for probabilistic bots"""

    def __init__(self, alpha: int):
        super().__init__()
        self.ship_layout = None
        self.D = None
        self.alpha = alpha
        self.starting_location = None
        self.bot_location = None
        self.sensory_data = List[SensoryData]
        self.traversal = []
        self.parent = {}
        self.open_cells = set()
        self.highest_p_cell = None

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_matrix = [
            [SensoryData() for _ in range(self.D)]
            for _ in range(self.D)
        ]

        for row in range(len(sensory_matrix)):
            for col in range(len(sensory_matrix)):
                if (
                    self.ship_layout[row][col] == Cell.CLOSED or self.ship_layout[row][col] == Cell.BOT
                ):
                    sensory_matrix[row][col].probability = 0.0
                elif self.ship_layout[row][col] != Cell.CLOSED:
                    self.open_cells.add((row, col))

        return sensory_matrix

    def path_to_highest_p_cell(
        self
    ) -> Optional[Tuple[List[List[int]]]]:
        """Returns the closest possible leak cell using BFS from bot's current location"""

        visited = set()
        queue = deque([self.bot_location])
        parent = {self.bot_location: self.bot_location}
        shortest_path = []

        while queue:
            row, col = queue.popleft()
            # Check the current cell
            if (row, col) == self.highest_p_cell:
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
                    and not self.sensory_data[d_row][d_col].invalid
                ):
                    queue.append((d_row, d_col))
                    parent[(d_row, d_col)] = (row, col)

        # If we found a reachable possible leak we reconstruct the path
        # which lead us there
        if shortest_path:
            while shortest_path[-1] != self.bot_location:
                r, c = parent[shortest_path[-1]]
                shortest_path.append((r, c))
            logging.debug(
                f"Path to highest p cell: {shortest_path.copy().reverse()}")
            return (
                shortest_path[0],
                shortest_path[-2],
            )  # (highest p cell, next step to get there)

        logging.debug("Path to highest p cell: None")
        return None  # Return None if no cell is found

    def print_sensory_data(self) -> None:
        """Outputs the current sensory data to the log"""

        precision = 5
        max_length = precision + 2
        sensory_output = "\n--Sensory Data--\n"
        for row in range(len(self.sensory_data)):
            for col in range(len(self.sensory_data)):
                if (row, col) == self.bot_location:
                    sensory_output += f"{'BOT'.ljust(max_length, ' ')}, "
                elif self.sensory_data[row][col].invalid:
                    sensory_output += f"{'INV'.ljust(max_length, ' ')}, "
                else:
                    sensory_output += f"{str(round(self.sensory_data[row][col].probability, precision)).ljust(max_length, ' ')}, "

            sensory_output = sensory_output.rsplit(", ", 1)[0]
            if row != len(self.ship_layout) - 1:
                sensory_output += "\n"

        logging.debug(sensory_output)

    def invalid_cell(self, row: int, col: int) -> None:
        """Returns true if cell is invalid"""

        open_neighbors = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            d_row, d_col = row + dr, col + dc
            if (
                d_row in range(self.D)
                and d_col in range(self.D)
                and self.ship_layout[d_row][d_col] != Cell.CLOSED
                and not self.sensory_data[d_row][d_col].invalid
            ):
                open_neighbors += 1

        return open_neighbors <= 1

    def print_distances(self) -> None:
        """Prints the distance map (for debugging purposes)"""

        output = "\n--Distance Map (Floyd-Warshall Algorithm)--"
        for key, value in self.distance.items():
            output += f"\nFrom {key}:"
            for target, distance in value.items():
                output += f"\n\tTo {target}: {distance}"

        logging.debug(output)
