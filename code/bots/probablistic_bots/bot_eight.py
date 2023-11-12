import logging
import random
import copy
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple, List
from config import Bots, Cell
from math import e
from .sensory_data import SensoryData
from collections import defaultdict


class BotEight(ProbabilisticBot):
    """

    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT8
        self.leaks_plugged = 0
        self.leak_locations = []
        self.sensory_data_matrix = []
        self.sensory_data_pairs_map = {}

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

    def setup(self) -> None:
        self.sensory_data_matrix = self.initialize_sensory_data_matrix()
        self.sensory_data_pairs_map = self.initialize_sensory_data_pairs_map()
        self.print_sensory_data_matrix()
        self.print_sensory_data_pairs_map()
        self.distance = self.get_distances()

    def initialize_sensory_data_matrix(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_data_matrix = [
            [SensoryData() for _ in range(self.D)]
            for _ in range(self.D)
        ]

        for row in range(self.D):
            for col in range(self.D):
                if not self.ship_layout[row][col] == Cell.CLOSED:
                    sensory_data_matrix[row][col].probability = 0.00
                    self.open_cells.add((row, col))

        return sensory_data_matrix

    def initialize_sensory_data_pairs_map(self) -> dict[dict[Tuple[int], float]]:
        """Returns a matrix representing the bot's initial sensory data"""
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
                self.sensory_data_matrix[row][col].probability += sensory_data_pairs_map[i][j]
        return sensory_data_pairs_map

    def sense(self) -> None:
        logging.debug(
            f"Bot did not find the leak in cell: {self.bot_location}")
        logging.debug(
            f"Updating probabilites given no leak in: {self.bot_location}")
        self.update_p_no_leak(self.bot_location[0], self.bot_location[1])
        self.print_sensory_data_pairs_map(
            f" [after update_p_no_leak({self.bot_location[0], self.bot_location[1]})]")
        self.print_sensory_data_matrix(
            f" [after update_p_no_leak({self.bot_location[0], self.bot_location[1]})]")

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
        self.print_sensory_data_matrix(" [after update_p_no_leak()]")
        self.print_sensory_data_pairs_map(" [after update_p_no_leak()]")

    def action(self, timestep: int) -> None:
        logging.debug(f"Timestep: {timestep}")
        if timestep % 2:
            self.move()
            self.moves += 1
        else:
            self.sense()
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

        self.sensory_data[r][c].probability = 0.00
        return self.bot_location

    def beep(self) -> Tuple[bool, float]:
        """
        Returns whether a beep occured and probability what the probability of the beep occuring was
        """

        leak_one = self.leak_locations[0]
        leak_two = self.leak_locations[1] if len(
            self.leak_locations) == 2 else None

        p_beep_one = e**(-self.alpha *
                         (self.distance[self.bot_location][leak_one]) - 1)
        p_beep_two = e**(-self.alpha *
                         (self.distance[self.bot_location][leak_two]) - 1) if leak_two else 0

        return ((random.random() < p_beep_one) or (random.random() < p_beep_two), p_beep_one + p_beep_two)

    def update_p_no_leak(self, row: int, col: int) -> None:
        """Returns updated sensory data given (row, col) does not contain the leak"""

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

        new_sensory_data_matrix = self.initialize_sensory_data_matrix()
        for i, values in self.sensory_data_pairs_map.items():
            for j in values:
                if i == j:
                    continue
                new_sensory_data_matrix[i[0]][i[1]
                                              ].probability += self.sensory_data_pairs_map[i][j]
        self.sensory_data_matrix = new_sensory_data_matrix
        self.sensory_data_matrix[row][col].probability = 0.00

    def update_p_beep(self) -> None:
        """
        P( leak in cell i and leak in cell j | beep in cell k )
            = P( beep in k | leak in cell i and leak in cell j ) * P( leak in cell i and leak in cell j ) / P( beep in cell k )

            P( beep in k | leak in cell i and leak in cell j )
                = e^(- a * (d(k,i) - 1)) + e^ - a * (d(k,j) - 1)) - e^ - a * (d(k,i) - 1)) * e^ - a * ( d(k,j) - 1) )

            P( leak in cell i and leak in cell j )
                = P( leak in cell i ) * P( leak in cell j )

            P( beep in cell k )
                = sum { cell l, cell m} P( leak in cell l and cell m AND beep in cell k)
                = sum { cell l, cell m} P( leak in cell l ) * P( leak in cell m ) * P( beep in cell k | leak in cell m and leak in cell l)

                    P( beep in cell k | leak in cell m and leak in cell l )
                        = e^(- a * (d(k,m) - 1)) + e^ - a * (d(k,l) - 1)) - e^ - a * (d(k,m) - 1)) * e^ - a * ( d(k,l) - 1) )

                = sum { cell l, cell m} P( leak in cell l ) * P( leak in cell m ) 
                    * e^(- a * (d(k,m) - 1)) + e^ - a * (d(k,l) - 1)) - e^ - a * (d(k,m) - 1)) * e^ - a * ( d(k,l) - 1) )

        P( leak in cell i and leak in cell j | beep in cell k )
            = P( beep in k | leak in cell i and leak in cell j ) * P( leak in cell i and leak in cell j ) / P( beep in cell k )
            = e^(- a * (d(k,i) - 1)) + e^ - a * (d(k,j) - 1)) - e^ - a * (d(k,i) - 1)) * e^ - a * ( d(k,j) - 1) )
                * P( leak in cell i ) * P( leak in cell j )
                    / sum { cell l, cell m} P( leak in cell l ) * P( leak in cell m ) 
                        * e^(- a * (d(k,m) - 1)) + e^ - a * (d(k,l) - 1)) - e^ - a * (d(k,m) - 1)) * e^ - a * ( d(k,l) - 1) )

        """
        sum_p_beep_in_cell_k = 0
        for l_row, l_col in self.open_cells:
            if (l_row, l_col) == (self.bot_location):
                continue

            p_leak_l = self.sensory_data[l_row][l_col].probability

            for m_row, m_col in self.open_cells:
                if (l_row, l_col) == (m_row, m_col):
                    continue

                p_leak_m = self.sensory_data[m_row][m_col].probability
                p_beep_m = e**(-self.alpha *
                               (self.distance[self.bot_location][(m_row, m_col)] - 1))
                p_beep_l = e**(-self.alpha *
                               (self.distance[self.bot_location][(l_row, l_col)] - 1))

                p_beep_k = (p_leak_l * p_leak_m) * \
                    ((p_beep_m + p_beep_l) - (p_beep_m * p_beep_l))

                sum_p_beep_in_cell_k += p_beep_k

        logging.critical(f"sum_p_beep_in_cell_k: {sum_p_beep_in_cell_k}")

        """
        P( beep in k | leak in cell i and leak in cell j )
            = e^(- a * (d(k,i) - 1)) + e^ - a * (d(k,j) - 1)) - e^ - a * (d(k,i) - 1)) * e^ - a * ( d(k,j) - 1) )
        P( leak in cell i and leak in cell j )
            = P( leak in cell i ) * P( leak in cell j )

        P( leak in cell i and leak in cell j | beep in cell k )
            = P( beep in k | leak in cell i and leak in cell j ) * P( leak in cell i and leak in cell j ) / P( beep in cell k )
            = e^(- a * (d(k,i) - 1)) + e^ - a * (d(k,j) - 1)) - e^ - a * (d(k,i) - 1)) * e^ - a * ( d(k,j) - 1) )
                * P( leak in cell i ) * P( leak in cell j )
                    / sum { cell l, cell m} P( leak in cell l ) * P( leak in cell m ) 
                        * e^(- a * (d(k,m) - 1)) + e^ - a * (d(k,l) - 1)) - e^ - a * (d(k,m) - 1)) * e^ - a * ( d(k,l) - 1) )
        """

    def update_p_no_beep(self) -> None:
        """
        --old shit--
        For cell i (our current cell): P( leak is in cell i | we heard no beep while in cell i ) = 0

        For cell j != i : P( leak is in cell j | we heard no beep while in cell i )
            =  P( leak in cell j ) * ( 1 - e^(-a*(d(i,j) - 1)) ) / [ sum_k P( leak is in k ) * ( 1 - e^(-a*(d(i,k)-1)) ) ]

        --new shit--
        P( leak in cell i and leak in cell j | no beep in cell k )
            = P( no beep in k | leak in cell i and leak in cell j ) * P( leak in cell i and leak in cell j ) / P( no beep in cell k )

        P( no beep in k | leak in cell i and leak in cell j )
            = (1 - e^(- a * (d(k,i) - 1))) + (1 - e^ - a * (d(k,j) - 1))) - (1 - e^ - a * (d(k,i) - 1))) * (1 - e^ - a * ( d(k,j) - 1) ))

        P( leak in cell i and leak in cell j )
            = P( leak in cell i ) * P( leak in cell j )

        P( no beep in cell k )
            = sum { cell l, cell m } P( leak in cell l AND cell m AND no beep in cell k)
            = sum { cell l, cell m } P( leak in cell l ) * P( leak in cell m ) * P( no beep in cell k | leak in cell m and leak in cell l)

                P( no beep in cell k | leak in cell m and leak in cell l )
                    = (1 - e^(- a * (d(k,m) - 1))) + (1 - e^ - a * (d(k,l) - 1))) - (1 - e^ - a * (d(k,m) - 1))) * (1 - e^ - a * ( d(k,l) - 1) ))

            = sum { cell l, cell m} P( leak in cell l ) * P( leak in cell m ) 
                * (1 - e^(- a * (d(k,m) - 1))) + (1 - e^ - a * (d(k,l) - 1))) - (1 - e^ - a * (d(k,m) - 1))) * (1 - e^ - a * ( d(k,l) - 1) ))

        """

        # Sum over all open cells; P( leak is in k ) * P( we heard no beep while in cell i )
        sum_p_no_beep_in_cell_k = 0
        for l_row, l_col in self.open_cells:
            # if (l_row, l_col) == (self.bot_location):
            #     continue

            p_leak_l = self.sensory_data_matrix[l_row][l_col].probability
            p_beep_l = 1 - e**(-self.alpha *
                               (self.distance[self.bot_location][(l_row, l_col)] - 1))

            for m_row, m_col in self.open_cells:
                # if (l_row, l_col) == (m_row, m_col):
                #     continue

                p_leak_m = self.sensory_data_matrix[m_row][m_col].probability
                p_beep_m = 1 - e**(-self.alpha *
                                   (self.distance[self.bot_location][(m_row, m_col)] - 1))

                p_beep_k = (p_leak_l * p_leak_m) * \
                    ((p_beep_m + p_beep_l) - (p_beep_m * p_beep_l))

                sum_p_no_beep_in_cell_k += p_beep_k

        logging.critical(f"sum_p_no_beep_in_cell_k: {sum_p_no_beep_in_cell_k}")

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2

    def print_sensory_data_matrix(self, msg: str = None) -> None:
        """Outputs the current sensory data to the log"""

        if not logging.DEBUG >= logging.root.level:
            return

        precision = 5
        max_length = precision + 2
        sensory_output = f"\n--Sensory Data Matrix { msg if msg else ''}--\n"
        for row in range(len(self.sensory_data_matrix)):
            for col in range(len(self.sensory_data_matrix)):
                if (row, col) == self.bot_location:
                    sensory_output += f"{'BOT'.ljust(max_length, ' ')}, "
                else:
                    sensory_output += f"{str(round(self.sensory_data_matrix[row][col].probability, precision)).ljust(max_length, ' ')}, "

            sensory_output = sensory_output.rsplit(", ", 1)[0]
            if row != len(self.ship_layout) - 1:
                sensory_output += "\n"

        sensory_data_matrix_sum = 0
        for row, col in self.open_cells:
            sensory_data_matrix_sum += self.sensory_data_matrix[row][col].probability

        logging.debug(sensory_output)
        logging.debug(f"Sensory data matrix sum: {sensory_data_matrix_sum}\n")

    def print_sensory_data_pairs_map(self, msg: str = None) -> None:
        """Outputs the current sensory data to the log"""

        if not logging.DEBUG >= logging.root.level:
            return

        precision = 5
        max_length = precision + 2
        sensory_output = f"\n--Sensory Data Pairs Map{ msg if msg else ''}--\n"
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
