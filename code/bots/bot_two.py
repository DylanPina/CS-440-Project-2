import logging
from .bot import Bot
from typing import Tuple, List, Optional
from config import Bots, Cell, SensoryData
from collections import deque


class BotTwo(Bot):
    """
    Performs the same as bot one until a leak has been found within the detection square. Once the 
    leak has been found, the bot will stop sensing and visit each and every open cell which has been marked.
    """

    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.variant = Bots.BOT2
        self.sensory_data = List[SensoryData]
        self.leak_found = False

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()

    def action(self, timestep: int) -> None:
        if self.leak_found or timestep % 2:
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
            self.sensory_data[r][c] = SensoryData.LEAK
            logging.debug(f"Bot has sensed the leak in its current cell!")
        else:
            self.sensory_data[r][c] = SensoryData.NO_LEAK
        return self.bot_location

    def sense(self) -> None:
        r, c = self.bot_location
        # Calculate the bounds of the square
        top, bottom = max(0, r - self.k), min(self.D, r + self.k + 1)
        left, right = max(0, c - self.k), min(self.D, c + self.k + 1)

        # Loop through each row of the square
        for row in range(top, bottom):
            for col in range(left, right):
                if self.ship_layout[row][col] == Cell.LEAK:
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
                elif self.sensory_data[row][col] != SensoryData.INVALID_CELL:
                    self.sensory_data[row][col] = SensoryData.NO_LEAK

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

        logging.debug(f"Closest {'proximity' if self.leak_found else 'possible leak'} cell: {closest_possible_leak_cell[0]}")
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
