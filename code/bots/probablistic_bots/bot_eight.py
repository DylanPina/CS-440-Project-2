import logging
import random
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple
from config import Bots, Cell
from math import e


class BotEight(ProbabilisticBot):
    """

    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT8
        self.leaks_plugged = 0
        self.leak_locations = set()

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

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

        leak_one, leak_two = self.leak_locations
        p_beep_one = e**(-self.alpha *
                         (self.distance[self.bot_location][leak_one]) - 1)
        p_beep_two = e**(-self.alpha *
                         (self.distance[self.bot_location][leak_two]) - 1)

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
        P( leak in cell j and leak in cell y | we heard a beep while in cell i )
            = P( leak in cell j and leak in cell y | beep in cell i ) / P ( beep in cell i)
            = P( leak in cell j | beep in cell i ) * P( leak in cell y | beep in cell i ) / P( beep in cell i )

            P( leak in cell j | beep in cell i )
                = P( beep in cell i | leak in cell j ) /  P( beep in cell i )
                = e^(-a*(d(i,j) - 1)) / sum_k P( leak in k ) *  e^(-a*(d(i,k)-1)) * for all k' != k P( leak in k' ) *  e^(-a*(d(i,k')-1))

            P( leak in cell y | beep in cell i )
                = P( beep in cell i | leak in cell y ) /  P( beep in cell i )
                = e^(-a*(d(i,y) - 1)) / sum_k P( leak in k ) *  e^(-a*(d(i,k)-1)) * for all k' != k P( leak in k' ) *  e^(-a*(d(i,k')-1))

        P( beep in cell i ) = sum_k P( leak in k AND beep in cell i ) * for all k' != k P( leak in k AND beep in cell i )
            = sum_k P( leak in k ) * P( beep in i | leak in k ) * for all k' != k P( leak in k' AND beep in cell i )
            = sum_k P( leak in k ) *  e^(-a*(d(i,k)-1)) * for all k' != k P( leak in k' AND beep in cell i )
            = sum_k P( leak in k ) *  e^(-a*(d(i,k)-1)) * for all k' != k P( leak in k' ) *  e^(-a*(d(i,k')-1))
        """

        # Sum over all open cells; P( leak in k ) *  P( we heard a beep while in cell i )
        sum_k_leak_beep = 0
        for k_row, k_col in self.open_cells:
            p_leak_in_k = self.sensory_data[k_row][k_col].probability * (
                e**(-self.alpha * (self.distance[self.bot_location][(k_row, k_col)] - 1)))
            for k_prime_row, k_prime_col in self.open_cells:
                p_leak_in_k_prime = self.sensory_data[k_prime_row][k_prime_row].probability * (
                    e**(-self.alpha * (self.distance[self.bot_location][(k_prime_row, k_prime_row)] - 1)))
                sum_k_leak_beep += p_leak_in_k * p_leak_in_k_prime

        logging.critical(f"sum_k_leak_beep: {sum_k_leak_beep}")

        for j_row, j_col in self.open_cells:
            if (j_row, j_col) == self.bot_location:
                continue

            p_leak_in_cell_j = self.sensory_data[j_row][j_col].probability
            p_beep_j = e**(-self.alpha *
                           (self.distance[self.bot_location][(j_row, j_col)] - 1))
            self.sensory_data[j_row][j_col].probability = (
                p_leak_in_cell_j * p_beep_j) / sum_k_leak_beep

    def update_p_no_beep(self) -> None:
        """
        For cell i (our current cell): P( leak is in cell i | we heard no beep while in cell i ) = 0

        For cell j != i : P( leak is in cell j | we heard no beep while in cell i )
            =  P( leak in cell j ) * ( 1 - e^(-a*(d(i,j) - 1)) ) / [ sum_k P( leak is in k ) * ( 1 - e^(-a*(d(i,k)-1)) ) ]
        """

        # Sum over all open cells; P( leak is in k ) * P( we heard no beep while in cell i )
        sum_k_leak_no_beep = 0
        for k_row, k_col in self.open_cells:
            sum_k_leak_no_beep += self.sensory_data[k_row][k_col].probability * \
                (1 - (e**(-self.alpha *
                          (self.distance[self.bot_location][(k_row, k_col)] - 1))))

        for j_row, j_col in self.open_cells:
            if (j_row, j_col) == self.bot_location:
                continue

            p_leak_in_cell_j = self.sensory_data[j_row][j_col].probability
            p_beep_j = e**(-self.alpha *
                           (self.distance[self.bot_location][(j_row, j_col)] - 1))
            p_not_beep_j = 1 - p_beep_j
            self.sensory_data[j_row][j_col].probability = (
                p_leak_in_cell_j * p_not_beep_j) / sum_k_leak_no_beep

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2
