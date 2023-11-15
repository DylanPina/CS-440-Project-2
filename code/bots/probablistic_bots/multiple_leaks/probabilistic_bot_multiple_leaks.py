import logging
import random
import copy
from typing import Tuple, List
from config import Cell
from math import e
from collections import defaultdict
from bots.probablistic_bots import ProbabilisticBot, SensoryData
from abc import ABC


class ProbabilisticBotMultipleLeaks(ProbabilisticBot, ABC):
    """Abstract base class for probabilistic bots"""

    def __init__(self, alpha: int):
        super().__init__(alpha)
        self.leaks_plugged = 0
        self.leak_locations = []
        self.sensory_data_pairs_map = {}

    def setup(self) -> None:
        self.sensory_data = self.initialize_sensory_data()
        self.sensory_data_pairs_map = self.initialize_sensory_data_pairs_map()
        self.print_sensory_data("initial")
        self.distance = self.get_distances()

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""
        sensory_data = [
            [SensoryData() for _ in range(self.D)]
            for _ in range(self.D)
        ]
        for row in range(self.D):
            for col in range(self.D):
                if not self.ship_layout[row][col] == Cell.CLOSED:
                    sensory_data[row][col].probability = 0.00
                    self.open_cells.add((row, col))
        return sensory_data

    def initialize_sensory_data_pairs_map(self) -> dict[dict[Tuple[int], float]]:
        """Returns a map representing the bot's initial cell pairing sensory data"""
        sensory_data_pairs_map = defaultdict(dict)
        n = len(self.open_cells)
        for i in self.open_cells:
            for j in self.open_cells:
                if i == j:
                    continue
                sensory_data_pairs_map[i][j] = 1 / (n * (n - 1))
        for i, values in sensory_data_pairs_map.items():
            row, col = i
            for j in values:
                if i == j:
                    continue
                self.sensory_data[row][col].probability += sensory_data_pairs_map[i][j]
        return sensory_data_pairs_map

    def sense_multi(self) -> None:
        """Updates sensory data about the environment for multiple leaks"""
        logging.debug(
            f"Bot did not find the leak in cell: {self.bot_location}")
        logging.debug(
            f"Updating probabilites given no leak in: {self.bot_location}")
        self.update_p_no_leak_multi(self.bot_location[0], self.bot_location[1])
        # self.print_sensory_data_pairs_map(
        #     f"[after update_p_no_leak({self.bot_location[0], self.bot_location[1]})]")
        self.print_sensory_data(
            f"[after update_p_no_leak({self.bot_location[0], self.bot_location[1]})]")
        beep, p_beep = self.beep()
        if beep:
            self.beeps += 1
            logging.debug(f"Beep with p_beep = {p_beep}")
            self.update_p_beep_multi()
            # self.print_sensory_data_pairs_map(
            #     f"[after update_p_beep({self.bot_location[0], self.bot_location[1]})]")
            self.print_sensory_data(
                f"[after update_p_beep({self.bot_location[0], self.bot_location[1]})]")
        else:
            self.no_beeps += 1
            logging.debug(f"No beep with p_beep = {p_beep}")
            self.update_p_no_beep_multi()
            # self.print_sensory_data_pairs_map(
            #     f"[after update_p_no_beep({self.bot_location[0], self.bot_location[1]})]")
            self.print_sensory_data(
                f"[after update_p_no_beep({self.bot_location[0], self.bot_location[1]})]")
        self.highest_p_cell = self.get_highest_p_cell(self.sensory_data)

    def action(self, timestep: int) -> None:
        logging.debug(f"Timestep: {timestep}")
        if timestep % 2:
            self.move()
            self.moves += 1
        else:
            if self.leaks_plugged:
                self.sense()
            else:
                self.sense_multi()
            self.senses += 1

    def move(self) -> Tuple[int]:
        # Move towards the closest possible leak cell
        self.bot_location = self.next_step()
        logging.debug(f"Bot has moved to {self.bot_location}")
        # Add the new location to the traversal
        if self.bot_location not in self.traversal:
            self.traversal.append(self.bot_location)
        # Check if move brought us to the leak cell
        r, c = self.bot_location
        if self.ship_layout[r][c] == Cell.LEAK:
            logging.debug(f"Bot has found a leak in its current cell")
            self.leaks_plugged += 1
            self.leak_locations.remove((r, c))
            self.ship_layout[r][c] = Cell.OPEN
            logging.debug(f"Leaks remaining: {2 - self.leaks_plugged}")
        return self.bot_location

    def beep(self) -> Tuple[bool, float]:
        """Returns whether a beep occured"""
        leak_one = self.leak_locations[0]
        leak_two = self.leak_locations[1] if len(
            self.leak_locations) == 2 else None
        p_beep_one = e**(-self.alpha *
                         (self.distance[self.bot_location][leak_one] - 1))
        p_beep_two = e**(-self.alpha *
                         (self.distance[self.bot_location][leak_two] - 1)) if leak_two else 0
        return ((random.random() <= p_beep_one) or (random.random() <= p_beep_two), 1 - ((1 - p_beep_one) * (1 - p_beep_two)))

    def update_p_no_leak_multi(self, row: int, col: int) -> None:
        """Returns updated sensory data given (row, col) does not contain the leak for multiple leaks"""
        leak_in_i_j = 0
        for i, values in self.sensory_data_pairs_map.items():
            for j in values:
                if i == j:
                    continue
                elif i == (row, col) or j == (row, col):
                    leak_in_i_j += self.sensory_data_pairs_map[i][j]
                    self.sensory_data_pairs_map[i][j] = 0.00
        for i, values in self.sensory_data_pairs_map.items():
            for j in values:
                if i == j:
                    continue
                self.sensory_data_pairs_map[i][j] /= 1 - leak_in_i_j
        for i, values in self.sensory_data_pairs_map.items():
            p = 0
            for j in values:
                if i == j:
                    continue
                p += self.sensory_data_pairs_map[i][j]
            self.sensory_data[i[0]][i[1]].probability = p
        self.sensory_data[row][col].probability = 0.00

    def update_p_beep_multi(self) -> None:
        """
        P( leak in cell i and leak in cell j | beep in cell k )
            = P( leak in cell i and leak in cell j )
                * P( beep in cell k | leak in cell i and leak in cell j )
                    / P( beep in cell k )
        """
        sum_p_beep_in_cell_k = 0
        for l_row, l_col in self.open_cells:
            if (l_row, l_col) == (self.bot_location):
                continue
            p_beep_l = e**(-self.alpha *
                           (self.distance[self.bot_location][(l_row, l_col)] - 1))
            for m_row, m_col in self.open_cells:
                if (l_row, l_col) == (m_row, m_col) or (m_row, m_col) == self.bot_location:
                    continue
                p_leak_l_m = self.sensory_data_pairs_map[(
                    l_row, l_col)][(m_row, m_col)]
                p_beep_m = e**(-self.alpha *
                               (self.distance[self.bot_location][(m_row, m_col)] - 1))
                p_beep_k = p_leak_l_m * \
                    ((p_beep_m + p_beep_l) - (p_beep_m * p_beep_l))
                sum_p_beep_in_cell_k += p_beep_k
        new_sensory_data_pairs_map = copy.deepcopy(self.sensory_data_pairs_map)
        for l_row, l_col in self.open_cells:
            if (l_row, l_col) == (self.bot_location):
                continue
            p_beep_l = e**(-self.alpha *
                           (self.distance[self.bot_location][(l_row, l_col)] - 1))
            for m_row, m_col in self.open_cells:
                if (l_row, l_col) == (m_row, m_col) or (m_row, m_col) == self.bot_location:
                    continue
                p_leak_l_m = self.sensory_data_pairs_map[(
                    l_row, l_col)][(m_row, m_col)]
                p_beep_m = e**(-self.alpha *
                               (self.distance[self.bot_location][(m_row, m_col)] - 1))
                new_sensory_data_pairs_map[(l_row, l_col)][(
                    m_row, m_col)] = p_leak_l_m * \
                    ((p_beep_m + p_beep_l) -
                     (p_beep_m * p_beep_l)) / sum_p_beep_in_cell_k
        self.sensory_data_pairs_map = new_sensory_data_pairs_map
        for i, values in self.sensory_data_pairs_map.items():
            p = 0
            for j in values:
                if i == j:
                    continue
                p += self.sensory_data_pairs_map[i][j]
            self.sensory_data[i[0]][i[1]].probability = p

    def update_p_no_beep_multi(self) -> None:
        """
        P( leak in cell i and leak in cell j | no beep in cell k )
            = P( leak in cell i and leak in cell j )
                * P( no beep in cell k | leak in cell i and leak in cell j )
                    / P( no beep in cell k )
        """
        for l_row, l_col in self.open_cells:
            if (l_row, l_col) == (self.bot_location):
                continue
            p_no_beep_l = 1 - e**(-self.alpha *
                                  (self.distance[self.bot_location][(l_row, l_col)] - 1))
            if not p_no_beep_l:
                self.update_p_no_leak_multi(l_row, l_col)
        sum_p_no_beep_in_cell_k = 0
        for l_row, l_col in self.open_cells:
            if (l_row, l_col) == (self.bot_location):
                continue
            p_no_beep_l = 1 - e**(-self.alpha *
                                  (self.distance[self.bot_location][(l_row, l_col)] - 1))
            for m_row, m_col in self.open_cells:
                if (l_row, l_col) == (m_row, m_col) or (m_row, m_col) == self.bot_location:
                    continue
                p_leak_l_m = self.sensory_data_pairs_map[(
                    l_row, l_col)][(m_row, m_col)]
                p_no_beep_m = 1 - e**(-self.alpha *
                                      (self.distance[self.bot_location][(m_row, m_col)] - 1))
                p_no_beep_k = p_leak_l_m * \
                    ((p_no_beep_m + p_no_beep_l) - (p_no_beep_m * p_no_beep_l))
                sum_p_no_beep_in_cell_k += p_no_beep_k
        new_sensory_data_pairs_map = copy.deepcopy(self.sensory_data_pairs_map)
        for l_row, l_col in self.open_cells:
            if (l_row, l_col) == (self.bot_location):
                continue
            p_no_beep_l = 1 - e**(-self.alpha *
                                  (self.distance[self.bot_location][(l_row, l_col)] - 1))
            for m_row, m_col in self.open_cells:
                if (l_row, l_col) == (m_row, m_col) or (m_row, m_col) == self.bot_location:
                    continue
                p_leak_l_m = self.sensory_data_pairs_map[(
                    l_row, l_col)][(m_row, m_col)]
                p_no_beep_m = 1 - e**(-self.alpha *
                                      (self.distance[self.bot_location][(m_row, m_col)] - 1))
                new_sensory_data_pairs_map[(l_row, l_col)][(
                    m_row, m_col)] = p_leak_l_m * \
                    ((p_no_beep_m + p_no_beep_l) -
                     (p_no_beep_m * p_no_beep_l)) / sum_p_no_beep_in_cell_k
        self.sensory_data_pairs_map = new_sensory_data_pairs_map
        for i, values in self.sensory_data_pairs_map.items():
            p = 0
            for j in values:
                if i == j:
                    continue
                p += self.sensory_data_pairs_map[i][j]
            self.sensory_data[i[0]][i[1]].probability = p

    def print_sensory_data_pairs_map(self, msg: str = None) -> None:
        """Outputs the current sensory data pairs map to the log"""
        if not logging.DEBUG >= logging.root.level:
            return
        precision = 5
        max_length = precision + 2
        sensory_output = f"\n--Sensory Data Pairs Map { msg if msg else ''}--\n"
        for i, values in self.sensory_data_pairs_map.items():
            sensory_output += f"{i[0], i[1]} -> ["
            if not values:
                sensory_output += f", "
            for j in values:
                sensory_output += f"{j[0], j[1]}: "
                sensory_output += f"{str(round(self.sensory_data_pairs_map[i][j], precision)).ljust(max_length, ' ')}, "
            sensory_output = sensory_output.rsplit(", ", 1)[0]
            sensory_output += "]\n"
        sensory_data_sum = 0
        for i, values in self.sensory_data_pairs_map.items():
            for j in values:
                sensory_data_sum += self.sensory_data_pairs_map[i][j]
        logging.debug(sensory_output)
        logging.debug(f"Sensory data pairs map sum: {sensory_data_sum}\n")

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2
