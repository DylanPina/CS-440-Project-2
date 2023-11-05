import logging
import random
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple, List, Optional
from config import Cell
from collections import deque, defaultdict
from math import e


class BotThree(ProbabilisticBot):
    """
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        # (row, col)[target_row, col] -> distance from (row, col) to (target_row, target_col)
        self.distance = {}
        self.p_beep = None  # Probability of beep occuring at current cell in current timestep

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()
        self.print_sensory_data()
        self.distance = self.get_distances()

    def action(self, timestep: int) -> None:
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
            self.sensory_data[r][c].probability = 1
            logging.debug(f"Bot has sensed the leak in its current cell!")
        else:
            self.sensory_data[r][c].probability = 0
        return self.bot_location

    def sense(self) -> None:
        beep, self.p_beep = self.beep()
        print(self.p_beep)
        if beep:
            logging.debug("BEEP!!!")
        else:
            logging.debug("No beep..")
        visited = set()
        queue = deque([self.bot_location])
        distance = 0

        while queue:
            row, col = queue.popleft()
            distance += 1

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
                    if self.sensory_data[d_row][d_col].probability:
                        self.sensory_data[d_row][d_col].probability = self.update_p(
                            beep, distance)
        self.print_sensory_data()

    def next_step(self) -> Optional[List[int]]:
        """"""

        pass

    def backtrack(self) -> List[int]:
        """
        Marks the current bot location as an invalid cell in the sensory data, removes the current location from the traversal, and returns the parent of the current location
        """

        r, c = self.bot_location
        self.sensory_data[r][c].invalid = True
        self.traversal.pop()
        return self.parent[self.bot_location]

    def beep(self) -> bool:
        """
        Returns whether a beep occured and probability what the probability of the beep occuring was
        P( beep in cell i ) = sum_k P( leak in k AND beep in cell i )
            = sum_k P( leak in k ) * P( beep in i | leak in k )
            = sum_k P( leak in k ) *  e^(-a*(d(i,k)-1))
        """

        i = self.bot_location
        p_beep = 0
        p_leak_k = 1 / (len(self.open_cells) - 1)

        for k in self.open_cells:
            if i in self.distance and k in self.distance[i]:
                p_beep += p_leak_k * \
                    e**(-self.alpha * (self.distance[i][k] - 1))
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

    def update_p(self, beep: bool, distance: int) -> float:
        """Returns the updated probability for a given cell"""

        # Probability of any open cell being the leak
        p_leak_in_cell_j = 1 / (len(self.open_cells) - 1)

        if beep:
            """
            P( leak is in cell j ) = 1 / (# open cells - 1)
            P( leak is in cell j | we heard a beep while in cell i )
                = P( leak in cell j ) * e^(-a*(d(i,j)-1)) / P( beep in cell i )
            """

            # Probability of recieving a beep at j (a cell some distance)
            p_beep_j = e**(-self.alpha * (distance - 1))
            return (p_leak_in_cell_j * p_beep_j) / self.p_beep
        else:
            """
            For cell i (our current cell): P( leak is in cell i | we heard no beep while in cell i ) = 0
            For cell j != i : P( leak is in cell j | we heard no beep while in cell i )
                =  P( leak in cell j ) * ( 1 - e^(-a*(d(i,j)-1)) ) / [ sum_k P( leak is in k ) * ( 1 - e^(-a*(d(i,k)-1)) ) ]
            """

            # Probability of not recieving a beep at j (a cell some distance)
            p_not_beep_j = 1 - e**(-self.alpha * (distance - 1))
            # Sum over all open cells; P( leak is in k ) * P( we heard no beep while in cell i )
            sum_k_leak_no_beep = 0
            for k in self.open_cells:
                sum_k_leak_no_beep += p_not_beep_j * \
                    1 - (e**(-self.alpha *
                             (self.distance[self.bot_location][k] - 1)))
            return (p_leak_in_cell_j / p_not_beep_j) / sum_k_leak_no_beep