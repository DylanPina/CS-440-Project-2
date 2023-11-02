from .bot import Bot
from typing import Tuple, List, Optional
from config import Bots, Cell, SensoryData
from collections import deque


class BotOne(Bot):
    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.variant = Bots.BOT1
        self.sensory_data = List[SensoryData]

    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        # Update the traversal
        self.traversal.append(self.bot_location)
        # Check if move brought us to the leak cell
        r, c = self.bot_location
        if self.ship_layout[r][c] == Cell.LEAK:
            self.sensory_data[r][c] = SensoryData.LEAK
            print(f"[INFO]: Bot has sensed the leak in its current cell!")
        else:
            self.sensory_data[r][c] = SensoryData.NO_LEAK
        return self.bot_location

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()

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

        print(sensory_output)

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
            print("[INFO]: Backtrack!")
            return self.backtrack()

        print(f"[INFO]: Closest possible leak cell: {closest_possible_leak_cell[0]}")
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
