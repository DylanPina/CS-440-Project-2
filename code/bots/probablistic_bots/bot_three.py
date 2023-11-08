import logging
import random
import copy
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple, List, Optional
from config import Cell, Bots
from collections import deque, defaultdict
from math import e
from .sensory_data import SensoryData


class BotThree(ProbabilisticBot):
    """
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        # (row, col)[target_row, col] -> distance from (row, col) to (target_row, target_col)
        self.variant = Bots.BOT3
        self.distance = {}
        self.p_beep = None  # Probability of beep occuring at current cell in current timestep

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()
        self.print_sensory_data()
        self.distance = self.get_distances()

    def action(self, timestep: int) -> None:
        logging.debug(f"Timestep: {timestep}")
        if timestep % 2:
            self.move()
        else:
            self.sense()

    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        logging.debug(f"Bot has moved to {self.bot_location}")
        # Update the traversal
        self.traversal.append(self.bot_location)
        # Check if move brought us to the leak cell
        r, c = self.bot_location
        if self.ship_layout[r][c] == Cell.LEAK:
            logging.debug(f"Bot has reached the leak!")
            logging.info(
                f"Beep rate: {self.beeps / (self.beeps + self.no_beeps)}")
        return self.bot_location

    def sense(self) -> None:
        logging.debug(
            f"Bot did not find the leak in cell: {self.bot_location}. Updating probabilites...")
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
        # Search for the path from current location to highest p cell (if any)
        path_to_highest_p_cell = self.path_to_highest_p_cell()

        next_step = path_to_highest_p_cell[1]
        self.parent[next_step] = self.bot_location
        return next_step

    def beep(self) -> Tuple[bool, float]:
        """
        Returns whether a beep occured and probability what the probability of the beep occuring was
        P( beep in cell i ) = sum_k P( leak in k AND beep in cell i )
            = sum_k P( leak in k ) * P( beep in i | leak in k )
            = sum_k P( leak in k ) *  e^(-a*(d(i,k)-1))
        """

        p_beep = e**(-self.alpha *
                     (self.distance[self.bot_location][self.leak_location] - 1))

        return (random.random() < p_beep, p_beep)

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
