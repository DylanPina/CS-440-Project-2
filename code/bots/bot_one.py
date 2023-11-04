import logging
from .bot import Bot
from typing import Tuple, List, Optional
from config import Bots, Cell, SensoryData
from collections import deque


class BotOne(Bot):
    """
    All cells outside the initial detection square start with the possibility of containing the leak
    (essentially, the bot starts having taken a sense action, and detected nothing). When the bot enters
    a cell (or starts in a cell), however, if it is not the leak cell, it is marked as not containing the leak. If the
    bot detects no leak in proximity - all cells in the detection square are marked as not containing the leak. If
    the bot detects a leak in proximity - all cells in the detection square not already marked as not containing the
    leak are marked as possibly containing the leak, and all cells outside the detection square are marked as not
    containing the leak. Note that if a single square remains that is marked as containing the leak and all others
    do not contain the leak - the leak must be in that one marked cell. Bot 1 acts in the following way:

        - At any time that has not detected a leak, it will proceed to the nearest cell that might contain the leak
          (breaking ties at random), enter it, and take the sense action, updating what it knows based on the results.
        - At any time that a leak has been detected, it will proceed to the nearest cell that might contain the leak,
          enter it, and in doing so either and the leak or rule that cell out.

    This proceeds until the leak is discovered.
    """

    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.variant = Bots.BOT1
        self.sensory_data = List[SensoryData]

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()

    def action(self, timestep: int) -> None:
        if timestep % 2 == 0:
            self.sense()
        elif timestep % 2 == 1:
            self.move()
            
    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        logging.debug(f"Bot has moved to {self.bot_location}")
        # Update the traversal
        self.traversal.append(self.bot_location)
        # Check if move brought us to the leak cell
        r, c = self.bot_location
        if self.ship_layout[r][c] == Cell.LEAK:
            self.sensory_data[r][c] = SensoryData.LEAK
            logging.debug("Bot has sensed the leak in its current cell")
        else:
            self.sensory_data[r][c] = SensoryData.NO_LEAK
        return self.bot_location

    def sense(self) -> None:
        r, c = self.bot_location
        leak_found = False
        # Calculate the bounds of the square
        top, bottom = max(0, r - self.k), min(self.D, r + self.k + 1)
        left, right = max(0, c - self.k), min(self.D, c + self.k + 1)

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

    def closest_possible_leak_cell(self) -> Optional[Tuple[List[List[int]]]]:
        """Returns the closest possible leak cell using BFS from bot's current location"""

        visited = set()
        queue = deque([self.bot_location])
        parent = {self.bot_location: self.bot_location}
        shortest_path = []

        while queue:
            row, col = queue.popleft()
            # Check the current cell
            if self.sensory_data[row][col] == SensoryData.POSSIBLE_LEAK:
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

    def next_step(self) -> Optional[List[int]]:
        closest_possible_leak_cell = self.closest_possible_leak_cell()
        # If we can't reach a possible leak from the current location we need to backtrack
        if not closest_possible_leak_cell:
            logging.debug("Backtrack!")
            return self.backtrack()

        logging.debug(f"Closest possible leak cell: {closest_possible_leak_cell[0]}")
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
