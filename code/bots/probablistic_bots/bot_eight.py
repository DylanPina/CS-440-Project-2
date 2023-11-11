import logging
import random
import copy
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple, List
from config import Bots, Cell
from math import e
from .sensory_data import SensoryData


class BotEight(ProbabilisticBot):
    """

    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT8
        self.leaks_plugged = 0
        self.leak_locations = []

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

    def initialize_sensory_data(self) -> List[List[SensoryData]]:
        """Returns a matrix representing the bot's initial sensory data"""

        sensory_matrix = [
            [SensoryData() for _ in range(self.D**2)]
            for _ in range(self.D**2)
        ]

        for row in range(len(sensory_matrix)):
            for col in range(len(sensory_matrix)):
                if not self.ship_layout[row][col] == Cell.CLOSED:
                    self.open_cells.add((row, col))
                else:
                    sensory_matrix[row][col].closed = True

        for row, col in self.open_cells:
            if not self.ship_layout[row][col] == Cell.BOT:
                sensory_matrix[row][col].probability = 1 / \
                    (len(self.open_cells) - 1)
            else:
                sensory_matrix[row][col].probability = 0.00

        return sensory_matrix

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
        """
        Returns updated sensory data given (row, col) does not contain the leak

        - You move (or dont hear a beep directly adjacent to) cell d
        - You do not find the leak
        - P(leak in d | leak not in d) = 0
        - What are P(leak in a | leak not in d), etc, for each cell?
            = P( leak in a | leak not in d )
            = P( leak in a and leak not in d ) / P( leak not in d )
            = P( leak in a ) * P( leak not in d | leak in a ) / P( leak not in d)
            = ( P( leak in a ) * 1 ) / P( leak not in d )
            = P( leak in a ) / ( 1 - P ( leak is in d ) )
        """

        leak_not_in_d = 1 - self.sensory_data[row][col].probability
        for r, c in self.open_cells:
            if (r, c) != (row, col):
                self.sensory_data[r][c].probability /= leak_not_in_d

        logging.debug(
            f"Divided all open cells by a constant factor of: {leak_not_in_d}")
        logging.debug(
            f"sensory_data[{row}][{col}].probability = {self.sensory_data[row][col].probability} -> 0.00")
        self.sensory_data[row][col].probability = 0.00

    def update_p_beep(self) -> None:
        """
        Bayes Theorem: P( A | B ) = P( B | A ) * P( A ) / P( B )
            P( A ) = P( leak in cell j and leak in cell y )
            P( B ) = P( we heard a beep while in cell i )

        --old shit--
        P( leak is in cell j | we heard a beep while in cell i )
            = P( leak in cell j ) * e^(-a*(d(i,j)-1)) / P( beep in cell i )
            = P( leak in cell j ) * e^(-a*(d(i,j)-1)) / sum_k P( leak in k ) *  e^(-a*(d(i,k)-1))

        --new shit--
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

        """
        sum { cell l, cell m} P( leak in cell l ) * P( leak in cell m ) 
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
        old_sensory_data = copy.deepcopy(self.sensory_data)
        for i_row, i_col in self.open_cells:
            if (i_row, i_col) == self.bot_location:
                continue

            p_leak_i = old_sensory_data[i_row][i_col].probability
            p_beep_i = e**(-self.alpha *
                           (self.distance[self.bot_location][(i_row, i_col)] - 1))

            for j_row, j_col in self.open_cells:
                if (l_row, l_col) == (j_row, j_col):
                    continue

                p_leak_j = old_sensory_data[j_row][j_col].probability
                p_beep_j = e**(-self.alpha *
                               (self.distance[(self.bot_location)][(j_row, j_col)] - 1))

                p_beep_k += p_leak_i * p_leak_j * p_beep_j + p_beep_i - p_beep_j * p_beep_i

            self.sensory_data[i_row][i_col].probability = p_beep_k / \
                sum_p_beep_in_cell_k

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
            if (l_row, l_col) == (self.bot_location):
                continue
            p_l = self.sensory_data[l_row][l_col].probability

            for m_row, m_col in self.open_cells:

                p_m = self.sensory_data[m_row][m_col].probability
                p_no_beep_m = 1 - e**(-self.alpha *
                                      (self.distance[self.bot_location][(m_row, m_col)] - 1))
                p_no_beep_l = 1 - e**(-self.alpha *
                                      (self.distance[self.bot_location][(l_row, l_col)] - 1))
                p_no_beep_k = (p_l * p_m) * \
                    ((p_no_beep_m + p_no_beep_l) - (p_no_beep_m * p_no_beep_l))

                sum_p_no_beep_in_cell_k += p_no_beep_k

        logging.critical(f"sum_p_no_beep_in_cell_k: {sum_p_no_beep_in_cell_k}")

        old_sensory_data = copy.deepcopy(self.sensory_data)
        for i_row, i_col in self.open_cells:
            p_leak_i = old_sensory_data[i_row][i_col].probability
            if (i_row, i_col) == self.bot_location:
                continue

            for j_row, j_col in self.open_cells:
                if (l_row, l_col) == (j_row, j_col):
                    continue

                p_leak_j = old_sensory_data[j_row][j_col].probability
                p_no_beep_i = 1 - e**(-self.alpha *
                                      (self.distance[self.bot_location][(i_row, i_col)] - 1))
                p_no_beep_j = 1 - e**(-self.alpha *
                                      (self.distance[self.bot_location][(j_row, j_col)] - 1))
                p_no_beep_k += p_leak_i * p_leak_j * \
                    (p_no_beep_j + p_no_beep_i) - (p_no_beep_j * p_no_beep_i)

            self.sensory_data[i_row][i_col].probability = p_no_beep_k / \
                sum_p_no_beep_in_cell_k

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2
