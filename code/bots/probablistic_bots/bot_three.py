import logging
import random
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple
from config import Bots, Cell
from math import e


class BotThree(ProbabilisticBot):
    """
    All cells (other than the bot's initial cell) start with equal probability of containing the leak. The nearer the bot is to the leak, the more likely it is to receive a beep. Bot 3 proceeds in the following way:

        - At any time, the bot is going to move to the cell that has the highest probability of containing the leak (breaking ties first by distance from the bot, then at random).
        - After entering any cell, if the cell does not contain a leak, the bot will take the sense action. Based on the results, it updates the probability of containing the leak for each cell.
        - After the beliefs are updated, this repeats, the bot proceeding to the cell that as the highest probability of containing the leak (breaking ties first by distance from the bot, then at random).
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT3
        self.leak_plugged = False

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
            logging.debug(f"Bot has reached the leak!")
            self.leak_plugged = True
        return self.bot_location

    def beep(self) -> Tuple[bool, float]:
        """
        Returns whether a beep occured and probability what the probability of the beep occuring was
        P( beep in cell i ) = sum_k P( leak in k AND beep in cell i )
            = sum_k P( leak in k ) * P( beep in i | leak in k )
            = sum_k P( leak in k ) *  e^(-a*(d(i,k)-1))
        """

        p_beep = e**(-self.alpha *
                     (self.distance[self.bot_location][self.leak_location] - 1))

        return (random.random() < p_beep, p_beep)

    def plugged_leaks(self) -> bool:
        return self.leak_plugged
