import logging
import random
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple
from config import Bots, Cell
from math import e


class BotSeven(ProbabilisticBot):
    """
    Bot 7 is exactly Bot 3, but removes the first leak once its cell is entered, anc continues until the 
    second leak is also identified and plugged.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT7
        self.leaks_plugged = 0
        self.leak_locations = []

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
        P( beep in cell i ) = sum_k P( leak in k AND beep in cell i )
            = sum_k P( leak in k ) * P( beep in i | leak in k )
            = sum_k P( leak in k ) *  e^(-a*(d(i,k)-1))
        """

        distance = float("inf")
        for l in self.leak_locations:
            if (self.distance[self.bot_location][l] - 1) < distance:
                distance = self.distance[self.bot_location][l] - 1

        p_beep = e**(-self.alpha * (distance))

        return (random.random() < p_beep, p_beep)

    def plugged_leaks(self) -> bool:
        return self.leaks_plugged == 2
