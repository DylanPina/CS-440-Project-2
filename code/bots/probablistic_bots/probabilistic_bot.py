import logging
from abc import ABC
from typing import List, Optional, Tuple
from config import Cell
from collections import deque, defaultdict
from bots import Bot
from .sensory_data import SensoryData
from math import e


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
        self.path_to_highest_p_cell = deque()
        self.beeps = 0
        self.no_beeps = 0
        self.p_beep = 0
        self.distance = {}
        self.moves = 0
        self.senses = 0

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()
        self.print_sensory_data()
        self.distance = self.get_distances()

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_matrix = [
            [SensoryData() for _ in range(self.D)]
            for _ in range(self.D)
        ]

        for row in range(len(sensory_matrix)):
            for col in range(len(sensory_matrix)):
                if not self.ship_layout[row][col] == Cell.CLOSED:
                    self.open_cells.add((row, col))
                else:
                    sensory_matrix[row][col].closed = True

        for row, col in self.open_cells:
            if not self.ship_layout[row][col] == Cell.BOT:
                sensory_matrix[row][col].probability = 1 / \
                    (len(self.open_cells) - 1)
            else:
                sensory_matrix[row][col].probability = 0.00

        return sensory_matrix

    def sense(self) -> None:
        logging.debug(
            f"Bot did not find the leak in cell: {self.bot_location}")
        logging.debug(
            f"Updating probabilites given no leak in: {self.bot_location}")
        self.update_p_no_leak(self.bot_location[0], self.bot_location[1])
        self.print_sensory_data(" [after update_p_no_leak()]")

        beep, self.p_beep = self.beep()
        if beep:
            self.beeps += 1
            logging.debug(f"Beep with p_beep: {self.p_beep}")
            self.update_p_beep()
        else:
            self.no_beeps += 1
            logging.debug(f"No beep with p_beep: {self.p_beep}")
            self.update_p_no_beep()

        self.highest_p_cell = self.get_highest_p_cell(self.sensory_data)
        self.print_sensory_data(" [after sense()]")

    def get_highest_p_cell(self, sensory_data: List[List[SensoryData]]) -> Tuple[SensoryData]:
        visited = set()
        queue = deque([self.bot_location])
        distance = 1
        highest_p = float('-inf')
        highest_p_cell = None

        while queue:
            row, col = queue.popleft()
            # Mark the cell as visited
            visited.add((row, col))
            # Add the neighboring cells to the queue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                d_row, d_col = row + dr, col + dc
                if (
                    d_row in range(self.D)
                    and d_col in range(self.D)
                    and (d_row, d_col) not in visited
                    and self.ship_layout[d_row][d_col] != Cell.CLOSED
                ):
                    queue.append((d_row, d_col))
                    if sensory_data[d_row][d_col].probability > highest_p:
                        highest_p = sensory_data[d_row][d_col].probability
                        highest_p_cell = (d_row, d_col)
            distance += 1

        return highest_p_cell

    def next_step(self) -> Optional[List[int]]:
        if not self.path_to_highest_p_cell:
            self.path_to_highest_p_cell = self.get_path_to_highest_p_cell()

        next_step = self.path_to_highest_p_cell.popleft()
        self.parent[next_step] = self.bot_location
        return next_step

    def get_distances(self):
        """Returns the shortest path from any node to any other node"""

        # Initialize the distances
        dist = defaultdict(dict)
        for i in range(self.D):
            for j in range(self.D):
                if self.ship_layout[i][j] != Cell.CLOSED:
                    for r in range(self.D):
                        for c in range(self.D):
                            if self.ship_layout[r][c] != Cell.CLOSED:
                                dist[(i, j)][(r, c)] = float('inf')
                    dist[(i, j)][(i, j)] = 0  # Distance to self is 0

        # Set initial distances for adjacent cells
        for i in range(self.D):
            for j in range(self.D):
                if self.ship_layout[i][j] != Cell.CLOSED:
                    # Directions: up, down, left, right
                    for dr, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dr, j + dy
                        if ni in range(self.D) and nj in range(self.D) and self.ship_layout[ni][nj] != Cell.CLOSED:
                            # Distance to adjacent open cells
                            dist[(i, j)][(ni, nj)] = 1

        # Floyd-Warshall algorithm
        for k in range(self.D):
            for l in range(self.D):
                if (k, l) in dist:  # Intermediate point
                    for i in range(self.D):
                        for j in range(self.D):
                            if (i, j) in dist:  # Start point
                                for m in range(self.D):
                                    for n in range(self.D):
                                        if (m, n) in dist:  # End point
                                            # Update the distance with the minimum value
                                            dist[(i, j)][(m, n)] = min(dist[(i, j)][(m, n)],
                                                                       dist[(i, j)][(k, l)] + dist[(k, l)][(m, n)])
        return dist

    def update_p_no_leak(self, row: int, col: int) -> None:
        """
        Returns updated sensory data given (row, col) does not contain the leak

        - You move (or dont hear a beep directly adjacent to) cell d
        - You do not find the leak
        - P(leak in d | leak not in d) = 0
        - What are P(leak in a | leak not in d), etc, for each cell?
            = P( leak in a | leak not in d )
            = P( leak in a and leak not in d ) / P( leak not in d )
            = P( leak in a ) * P( leak not in d | leak in a ) / P( leak not in d)
            = ( P( leak in a ) * 1 ) / P( leak not in d )
            = P( leak in a ) / ( 1 - P ( leak is in d ) )
        """

        leak_not_in_d = 1 - self.sensory_data[row][col].probability
        if leak_not_in_d != 1:
            for r, c in self.open_cells:
                if (r, c) != (row, col):
                    self.sensory_data[r][c].probability /= leak_not_in_d

        logging.debug(
            f"Divided all open cells by a constant factor of: {leak_not_in_d}")
        logging.debug(
            f"sensory_data[{row}][{col}].probability = {self.sensory_data[row][col].probability} -> 0.00")
        self.sensory_data[row][col].probability = 0.00

    def update_p_beep(self) -> None:
        """
        P( leak is in cell j | we heard a beep while in cell i )
            = P( leak in cell j ) * e^(-a*(d(i,j)-1)) / P( beep in cell i )
            = P( leak in cell j ) * e^(-a*(d(i,j)-1)) / sum_k P( leak in k ) *  e^(-a*(d(i,k)-1))
        """

        # Sum over all open cells; P( leak in k ) *  P( we heard a beep while in cell i )
        sum_k_leak_beep = 0
        for k_row, k_col in self.open_cells:
            sum_k_leak_beep += self.sensory_data[k_row][k_col].probability * \
                (e**(-self.alpha *
                     (self.distance[self.bot_location][(k_row, k_col)] - 1)))

        # new_sensory_data = copy.deepcopy(self.sensory_data)
        for j_row, j_col in self.open_cells:
            if (j_row, j_col) == self.bot_location:
                continue

            p_leak_in_cell_j = self.sensory_data[j_row][j_col].probability
            p_beep_j = e**(-self.alpha *
                           (self.distance[self.bot_location][(j_row, j_col)] - 1))
            self.sensory_data[j_row][j_col].probability = (
                p_leak_in_cell_j * p_beep_j) / sum_k_leak_beep

    def update_p_no_beep(self) -> None:
        """
        For cell i (our current cell): P( leak is in cell i | we heard no beep while in cell i ) = 0

        For cell j != i : P( leak is in cell j | we heard no beep while in cell i )
            =  P( leak in cell j ) * ( 1 - e^(-a*(d(i,j) - 1)) ) / [ sum_k P( leak is in k ) * ( 1 - e^(-a*(d(i,k)-1)) ) ]
        """

        # Sum over all open cells; P( leak is in k ) * P( we heard no beep while in cell i )
        sum_k_leak_no_beep = 0
        for k_row, k_col in self.open_cells:
            sum_k_leak_no_beep += self.sensory_data[k_row][k_col].probability * \
                (1 - (e**(-self.alpha *
                          (self.distance[self.bot_location][(k_row, k_col)] - 1))))

        for j_row, j_col in self.open_cells:
            if (j_row, j_col) == self.bot_location:
                continue

            p_leak_in_cell_j = self.sensory_data[j_row][j_col].probability
            p_beep_j = e**(-self.alpha *
                           (self.distance[self.bot_location][(j_row, j_col)] - 1))
            p_not_beep_j = 1 - p_beep_j
            self.sensory_data[j_row][j_col].probability = (
                p_leak_in_cell_j * p_not_beep_j) / sum_k_leak_no_beep

    def get_path_to_highest_p_cell(self) -> deque[Tuple[int]]:
        """Returns the closest possible leak cell using BFS from bot's current location"""

        visited = set()
        queue = deque([self.bot_location])
        parent = {self.bot_location: self.bot_location}
        shortest_path = deque()

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
                    and self.ship_layout[d_row][d_col] != Cell.CLOSED
                ):
                    queue.append((d_row, d_col))
                    parent[(d_row, d_col)] = (row, col)

        # If we found a reachable possible leak we reconstruct the path
        # which lead us there
        if shortest_path:
            while shortest_path[-1] != self.bot_location:
                r, c = parent[shortest_path[-1]]
                shortest_path.append((r, c))
            shortest_path.reverse()
            logging.debug(
                f"Path to highest p cell: {shortest_path}")
            # (highest p cell, next step to get there)
            shortest_path.popleft()
            return shortest_path

        logging.debug("Path to highest p cell: None")
        return None  # Return None if no cell is found

    def print_sensory_data(self, msg: str = None) -> None:
        """Outputs the current sensory data to the log"""

        if not logging.DEBUG >= logging.root.level:
            return

        precision = 5
        max_length = precision + 2
        sensory_output = f"\n--Sensory Data{ msg if msg else ''}--\n"
        for row in range(len(self.sensory_data)):
            for col in range(len(self.sensory_data)):
                if (row, col) == self.bot_location:
                    sensory_output += f"{'BOT'.ljust(max_length, ' ')}, "
                else:
                    sensory_output += f"{str(round(self.sensory_data[row][col].probability, precision)).ljust(max_length, ' ')}, "

            sensory_output = sensory_output.rsplit(", ", 1)[0]
            if row != len(self.ship_layout) - 1:
                sensory_output += "\n"

        sensory_data_sum = 0
        for row, col in self.open_cells:
            sensory_data_sum += self.sensory_data[row][col].probability

        logging.debug(sensory_output)
        logging.debug(f"Sensory data sum: {sensory_data_sum}\n")

    def print_distances(self) -> None:
        """Prints the distance map (for debugging purposes)"""

        if not logging.DEBUG >= logging.root.level:
            return

        output = "\n--Distance Map (Floyd-Warshall Algorithm)--"
        for key, value in self.distance.items():
            output += f"\nFrom {key}:"
            for target, distance in value.items():
                output += f"\n\tTo {target}: {distance}"

        logging.debug(output)

    def print_stats(self, timestep: int) -> None:
        logging.info(f"Bot has found the leak at timestep: {timestep}")
        logging.info(
            f"Beep rate: {self.beeps / (self.beeps + self.no_beeps)}")
        logging.info(f"Moves: {self.moves}")
        logging.info(f"Senses: {self.senses}")
