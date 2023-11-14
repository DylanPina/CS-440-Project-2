import logging
from math import floor
from .deterministic_bot import DeterministicBot
from typing import Tuple, List, Optional
from config import Bots, Cell
from .sensory_data import SensoryData


class BotFive(DeterministicBot):
    """
    Bot 5 is exactly Bot 1, but removes the first leak once its cell is entered, and continues until the second leak is also identified and plugged.
    """

    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.variant = Bots.BOT5
        self.leaks_plugged = 0
        self.leak_locations = []

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"K value: {self.k}")

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()

    def action(self, timestep: int) -> None:
        if timestep % 2 == 0:
            self.sense()
            self.senses += 1
        elif timestep % 2 == 1:
            self.move()
            self.moves += 1

    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        logging.debug(f"Bot has moved to {self.bot_location}")
        # Update the traversal
        self.traversal.append(self.bot_location)
        # Check if move brought us to the leak cell
        r, c = self.bot_location
        if self.ship_layout[r][c] == Cell.LEAK:
            logging.debug("Bot has found a leak in its current cell")
            self.leaks_plugged += 1
            logging.debug(f"Leaks remaining: {2 - self.leaks_plugged}")

        self.sensory_data[r][c] = SensoryData.NO_LEAK
        return self.bot_location

    def sense(self) -> None:
        r, c = self.bot_location
        leak_found = False
        # Calculate the bounds of the square
        top, bottom = floor(
            max(0, r - self.k)), floor(min(self.D, r + self.k + 1))
        left, right = floor(
            max(0, c - self.k)), floor(min(self.D, c + self.k + 1))

        # Loop through each row of the square
        for row in range(top, bottom):
            for col in range(left, right):
                if self.ship_layout[row][col] == Cell.LEAK:
                    leak_found = True

        # If the leak is not found then we update the sensory data square
        # with all the cells in the square to NO LEAK
        if not leak_found:
            for row in range(top, bottom):
                for col in range(left, right):
                    self.sensory_data[row][col] = SensoryData.NO_LEAK

        self.print_sensory_data()

    def next_step(self) -> Optional[List[int]]:
        # Search for the closest possible leak cell (if any)
        closest_possible_leak_cell = self.closest_possible_leak_cell(
            SensoryData.POSSIBLE_LEAK)
        # If we can't reach a possible leak from the current location we need to backtrack
        if not closest_possible_leak_cell:
            logging.debug("Backtrack!")
            return self.backtrack()

        logging.debug(
            f"Closest possible leak cell: {closest_possible_leak_cell[0]}")
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

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2
