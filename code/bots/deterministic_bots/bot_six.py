import logging
from math import floor
from .deterministic_bot import DeterministicBot
from typing import Tuple, List, Optional
from config import Bots, Cell
from .sensory_data import SensoryData


class BotSix(DeterministicBot):
    """Modified veresion of bot two to handle two leaks"""

    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.variant = Bots.BOT6
        self.leak_found = False
        self.leaks_plugged = 0
        self.leak_locations = []

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"K value: {self.k}")

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()

    def action(self, timestep: int) -> None:
        if self.leak_found or timestep % 2:
            self.move()
            self.moves += 1
        else:
            self.sense()
            self.senses += 1

    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        logging.debug(f"Bot has moved to {self.bot_location}")
        self.print_sensory_data()
        # Update the traversal
        self.traversal.append(self.bot_location)
        # Check if move brought us to the leak cell
        r, c = self.bot_location
        if self.ship_layout[r][c] == Cell.LEAK:
            logging.debug("Bot has found a leak in its current cell")
            self.sensory_data[r][c] = SensoryData.LEAK
            self.ship_layout[r][c] = Cell.OPEN
            self.leaks_plugged += 1
            logging.debug(f"Leaks remaining: {2 - self.leaks_plugged}")
            self.leak_found = False
            self.clear_invalid_cells()
            self.traversal = []
        else:
            self.sensory_data[r][c] = SensoryData.NO_LEAK

        return self.bot_location

    def sense(self) -> None:
        r, c = self.bot_location
        # Calculate the bounds of the square
        top, bottom = floor(
            max(0, r - self.k)), floor(min(self.D, r + self.k + 1))
        left, right = floor(
            max(0, c - self.k)), floor(min(self.D, c + self.k + 1))

        # Loop through each row of the square
        for row in range(top, bottom):
            for col in range(left, right):
                if self.ship_layout[row][col] == Cell.LEAK and not self.sensory_data[row][col] == SensoryData.LEAK:
                    self.leak_found = True

        # If the leak is not found then we update the sensory data square
        # with all the cells in the square to NO LEAK
        for row in range(top, bottom):
            for col in range(left, right):
                if (
                    self.leak_found
                    and self.sensory_data[row][col] == SensoryData.POSSIBLE_LEAK
                ):
                    self.sensory_data[row][col] = SensoryData.IN_PROXIMITY
                elif (self.sensory_data[row][col] == SensoryData.POSSIBLE_LEAK):
                    self.sensory_data[row][col] = SensoryData.NO_LEAK

        self.print_sensory_data()

    def next_step(self) -> Optional[List[int]]:
        # If the leak has been found then we will just up dog it to the closest cell in proximity of the leak
        closest_possible_leak_cell = None
        if self.leak_found:
            closest_possible_leak_cell = self.closest_possible_leak_cell(
                SensoryData.IN_PROXIMITY
            )
        # If we can't find any cells marked in proximity of the leak, resort to cells marked as possible leak cells
        else:
            closest_possible_leak_cell = self.closest_possible_leak_cell(
                SensoryData.POSSIBLE_LEAK
            )
        # If we can't reach a possible leak from the current location we need to backtrack to a previous cell
        if not closest_possible_leak_cell:
            logging.debug("Backtrack!")
            return self.backtrack()

        logging.debug(
            f"Closest {'proximity' if self.leak_found else 'possible leak'} cell: {closest_possible_leak_cell[0]}")
        next_step = closest_possible_leak_cell[1]
        self.parent[next_step] = self.bot_location
        return next_step

    def backtrack(self) -> List[int]:
        """
        Marks the current bot location as an invalid cell in the sensory data, removes the current
        location from the traversal, and returns the parent of the current location
        """

        r, c = self.bot_location
        self.sensory_data[r][c] = SensoryData.INVALID_CELL
        self.traversal.pop()
        return self.parent[self.bot_location]

    def clear_invalid_cells(self) -> None:
        """Clears all invalid cells from the sensory data"""

        for row in range(len(self.sensory_data)):
            for col in range(len(self.sensory_data)):
                if self.sensory_data[row][col] == SensoryData.INVALID_CELL:
                    self.sensory_data[row][col] = SensoryData.POSSIBLE_LEAK

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2
