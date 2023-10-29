from .bot import Bot
from typing import Tuple, List, Optional
from config import Bots, Cell, SensoryData
from collections import deque


class BotOne(Bot):

    def __init__(self, k: int) -> None:
        super().__init__(k)
        self.variant = Bots.BOT1
        self.sensory_data = []

    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        # Update the traversal
        self.traversal.append(self.bot_location)
        return self.bot_location

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()

    def sense(self) -> None:
        r, c = self.bot_location
        square_traversal = []
        leak_found = False

        # Calculate the bounds of the square
        top, bottom = max(0, r - self.k), min(self.D, r + self.k + 1)
        left, right = max(0, c - self.k), min(self.D, c + self.k + 1)

        # Initialize variables to keep track of the direction of traversal
        direction = 1  # 1 for right, -1 for left

        # Loop through each row of the square
        for row in range(top, bottom):
            # If direction is 1, traverse from left to right
            if direction == 1:
                for col in range(left, right):
                    if self.ship_layout[row][col] == Cell.LEAK:
                        leak_found = True
                    square_traversal.append((row, col))
            # If direction is -1, traverse from right to left
            else:
                for col in range(right - 1, left - 1, -1):
                    if self.ship_layout[row][col] == Cell.LEAK:
                        leak_found = True
                    square_traversal.append((row, col))
            # Change the direction of traversal
            direction *= -1

        # If the leak is not found then we update the sensory data square
        # with all the cells in the square to NO LEAK
        if not leak_found:
            for row in range(left, right):
                if direction == 1:
                    for col in range(left, right):
                        self.sensory_data[row][col] = SensoryData.NO_LEAK
                # If direction is -1, traverse from right to left
                else:
                    for col in range(right - 1, left - 1, -1):
                        self.sensory_data[row][col] = SensoryData.NO_LEAK
                direction *= -1

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_matrix = [[SensoryData.NO_LEAK] *
                          len(self.ship_layout) for _ in range(len(self.ship_layout))]

        for row in range(len(self.ship_layout)):
            for col in range(len(self.ship_layout)):
                if self.ship_layout[row][col] == Cell.OPEN or self.ship_layout[row][col] == Cell.LEAK:
                    sensory_matrix[row][col] = SensoryData.POSSIBLE_LEAK

        return sensory_matrix

    def print_sensory_data(self) -> None:
        """Prints the current sensory data to the console"""

        output = "--Sensory Data--\n"
        for row in range(len(self.sensory_data)):
            for col in range(len(self.sensory_data)):
                output += f"{self.sensory_data[row][col].value}, "

            output = output.rsplit(", ", 1)[0]
            if row != len(self.ship_layout) - 1:
                output += "\n"

        print(output)

    def closest_possible_leak_cell(self) -> Optional[List[int]]:
        """Returns the closest possible leak cell from bots current location using BFS"""

        visited = set()
        queue = deque([self.bot_location])

        while queue:
            row, col = queue.popleft()

            # Check the current cell
            if self.sensory_data[row][col] == SensoryData.POSSIBLE_LEAK:
                return [row, col]

            # Mark the cell as visited
            visited.add((row, col))
            # Add the neighboring cells to the queue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                d_row, d_col = row + dr, col + dc
                if d_row in range(self.D) and d_col in range(self.D) and not (d_row, d_col) not in visited:
                    queue.append((d_row, d_col))

        return None  # Return None if no cell is found

    def next_step(self) -> Optional[List[int]]:
        current_row, current_col = self.bot_location
        closest_possible_leak_cell = self.closest_possible_leak_cell()

        # If we can't get to any possible leak cells we will just return the next
        # valid step we can take
        if not closest_possible_leak_cell:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                d_row, d_col = current_row + dr, current_col + dc
                if d_row in range(self.D) and d_col in range(self.D) and not (d_row, d_col) in self.traversal:
                    return [d_row, d_col]

        # Determine the direction to move which puts us as close as possible to
        # the next possible leak cell
        target_row, target_col = closest_possible_leak_cell
        if current_row < target_row:  # Move Down
            return (min(current_row + 1, self.D - 1), current_col)
        elif current_row > target_row:  # Move Up
            return (max(current_row - 1, 0), current_col)
        elif current_col < target_col:  # Move Right
            return (current_row, min(current_col + 1, self.D - 1))
        elif current_col > target_col:  # Move Left
            return (current_row, max(current_col - 1, 0))
