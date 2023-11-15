import logging
import random
from .probabilistic_bot_multiple_leaks import ProbabilisticBotMultipleLeaks
from typing import Tuple, List, Optional
from config import Bots, Quadrant, Cell
from math import e, ceil
from collections import deque


class BotNine(ProbabilisticBotMultipleLeaks):
    """

    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT9
        self.current_quadrant: Optional[Quadrant] = None
        self.q_1 = Quadrant(name="Quadrant 1", cells=set())
        self.q_2 = Quadrant(name="Quadrant 2", cells=set())
        self.q_3 = Quadrant(name="Quadrant 3", cells=set())
        self.q_4 = Quadrant(name="Quadrant 4", cells=set())
        self.highest_p_cell_in_quadrant: Optional[Tuple[int]] = None
        self.quadrant_p_thresold = 0

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

    def setup(self) -> None:
        super().setup()
        self.divide_board()
        logging.debug(f"Quadrant I: {self.q_1} - length: {len(self.q_1)}")
        logging.debug(f"Quadrant II: {self.q_2} - length: {len(self.q_2)}")
        logging.debug(f"Quadrant III: {self.q_3} - length: {len(self.q_3)}")
        logging.debug(f"Quadrant IV: {self.q_4} - length: {len(self.q_4)}")

    def sense(self) -> None:
        logging.debug(
            f"Bot did not find the leak in cell: {self.bot_location}")
        logging.debug(
            f"Updating probabilites given no leak in: {self.bot_location}")
        self.update_p_no_leak(self.bot_location[0], self.bot_location[1])
        self.print_sensory_data(
            f" [after update_p_no_leak{self.bot_location}]")

        if self.current_quadrant and (self.current_quadrant_p_sum() <= self.quadrant_p_thresold):
            logging.debug(
                f"Current quadrant: {self.current_quadrant} is being set to None")
            self.current_quadrant = None

        beep, self.p_beep = self.beep()
        if beep:
            self.beeps += 1
            logging.debug(f"Beep with p_beep: {self.p_beep}")
            self.update_p_beep()
        else:
            self.no_beeps += 1
            logging.debug(f"No beep with p_beep: {self.p_beep}")
            self.update_p_no_beep()

        if not self.current_quadrant:
            self.current_quadrant = self.get_highest_p_quadrant()
            logging.debug(f"New current quadrant {self.current_quadrant.name}")

        self.highest_p_cell_in_quadrant = self.get_highest_p_cell_in_quadrant(
            self.current_quadrant.cells)
        self.print_sensory_data(f" [after sense({self.bot_location})]")

    def sense_multi(self) -> None:
        """Updates sensory data about the environment for multiple leaks"""
        logging.debug(
            f"Bot did not find the leak in cell: {self.bot_location}")
        logging.debug(
            f"Updating probabilites given no leak in: {self.bot_location}")
        self.update_p_no_leak_multi(self.bot_location[0], self.bot_location[1])
        self.print_sensory_data(
            f"[after update_p_no_leak({self.bot_location[0], self.bot_location[1]})]")

        if self.current_quadrant and (self.current_quadrant_p_sum() <= self.quadrant_p_thresold):
            logging.debug(
                f"Current quadrant: {self.current_quadrant} is being set to None")
            self.current_quadrant = None

        beep, p_beep = self.beep()
        if beep:
            self.beeps += 1
            logging.debug(f"Beep with p_beep = {p_beep}")
            self.update_p_beep_multi()
            self.print_sensory_data(
                f"[after update_p_beep({self.bot_location[0], self.bot_location[1]})]")
        else:
            self.no_beeps += 1
            logging.debug(f"No beep with p_beep = {p_beep}")
            self.update_p_no_beep_multi()
            self.print_sensory_data(
                f"[after update_p_no_beep({self.bot_location[0], self.bot_location[1]})]")

        if not self.current_quadrant:
            self.current_quadrant = self.get_highest_p_quadrant()
            logging.debug(f"New current quadrant {self.current_quadrant.name}")

        self.highest_p_cell_in_quadrant = self.get_highest_p_cell_in_quadrant(
            self.current_quadrant.cells)
        self.print_sensory_data(f" [after sense({self.bot_location})]")

    def current_quadrant_p_sum(self) -> float:
        """Returns the cummulative probability sum of the current quadrant"""

        current_quadrant_sum = 0
        for row, col in self.current_quadrant.cells:
            current_quadrant_sum += self.sensory_data[row][col].probability
        return current_quadrant_sum

    def get_highest_p_quadrant(self) -> Quadrant:
        """Returns the quadrant with highest cummulative probability sum"""

        quad_one_sum = quad_two_sum = quad_three_sum = quad_four_sum = 0

        for row, col in self.q_1.cells:
            quad_one_sum += self.sensory_data[row][col].probability
        for row, col in self.q_2.cells:
            quad_two_sum += self.sensory_data[row][col].probability
        for row, col in self.q_3.cells:
            quad_three_sum += self.sensory_data[row][col].probability
        for row, col in self.q_4.cells:
            quad_four_sum += self.sensory_data[row][col].probability

        if quad_one_sum >= max(quad_two_sum, quad_three_sum, quad_four_sum):
            return self.q_1
        elif quad_two_sum >= max(quad_one_sum, quad_three_sum, quad_four_sum):
            return self.q_2
        elif quad_three_sum >= max(quad_one_sum, quad_two_sum, quad_four_sum):
            return self.q_3
        else:
            return self.q_4

    def get_highest_p_cell_in_quadrant(self, quadrant_cells: set) -> Tuple[int, int]:
        """
        Returns the cell in the quadrant with the highest probability of containing leak and closest to the bot's current location
        """

        highest_p = float('-inf')
        highest_p_cell = None

        for row, col in quadrant_cells:
            if self.sensory_data[row][col].probability >= highest_p:
                highest_p = self.sensory_data[row][col].probability
                highest_p_cell = (row, col)

        return highest_p_cell

    def get_path_to_cell(self, target_row: int, target_col: int) -> deque[Tuple[int]]:
        """Returns the closest possible leak cell using BFS from bot's current location"""

        visited = set()
        queue = deque([self.bot_location])
        parent = {self.bot_location: self.bot_location}
        shortest_path = deque()

        while queue:
            row, col = queue.popleft()
            # Check the current cell
            if (row, col) == (target_row, target_col):
                shortest_path.append((row, col))
                break

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

    def next_step(self) -> Optional[List[int]]:
        if not self.path_to_highest_p_cell:
            r, c = self.highest_p_cell_in_quadrant = self.get_highest_p_cell_in_quadrant(
                self.current_quadrant.cells)
            self.path_to_highest_p_cell = self.get_path_to_cell(r, c)

        next_step = self.path_to_highest_p_cell.popleft()
        self.parent[next_step] = self.bot_location
        return next_step

    def divide_board(self) -> None:
        """Divides board into four quandrants"""

        # Divide board for even D val
        if self.D % 2 == 0:
            for row, col in self.open_cells:
                if row in range(0, self.D // 2):
                    if col in range(0, self.D // 2):
                        self.q_1.cells.add((row, col))
                    else:
                        self.q_2.cells.add((row, col))
                else:
                    if col in range(0, self.D // 2):
                        self.q_3.cells.add((row, col))
                    else:
                        self.q_4.cells.add((row, col))
        # Divide board for odd D val
        else:
            for row, col in self.open_cells:
                if row in range(0, self.D // 2) and col in range(self.D // 2, self.D):
                    self.q_2.cells.add((row, col))
                elif row == self.D // 2 and col == self.D // 2:
                    self.q_2.cells.add((row, col))
                elif row in range(0, self.D // 2 + 1) and col in range(0, self.D // 2):
                    self.q_1.cells.add((row, col))
                elif row in range(ceil(self.D / 2), self.D) and col in range(0, self.D // 2 + 1):
                    self.q_3.cells.add((row, col))
                elif row in range(self.D // 2, self.D) and col in range(ceil(self.D / 2), self.D):
                    self.q_4.cells.add((row, col))
