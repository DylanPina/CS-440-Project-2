import logging
import random
from .probabilistic_bot import ProbabilisticBot
from typing import Tuple
from config import Bots, Cell
from math import e, floor, ceil


class BotFour(ProbabilisticBot):
    """
    Similar to bot 3 in regards to having a probabilistic leak detector and how it proceeds to find the leak. However, this bot will wait two timesteps of sensing before moving inorder to collect more data about its surroundings before constructing a path to the cell with the highest probability. By this adjustment, the bot will have more information before it starts traversing down a path and is less likely to waste time going down the wrong path.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT4
        self.leak_plugged = False
        self.q_1 = set()
        self.q_2 = set()
        self.q_3 = set()
        self.q_4 = set()

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

    def setup(self) -> None:
        super().setup()
        self.divide_board()
        logging.debug(f"Quadrant I: {self.q_1}")
        logging.debug(f"Quadrant II: {self.q_2}")
        logging.debug(f"Quadrant III: {self.q_3}")
        logging.debug(f"Quadrant IV: {self.q_4}")

    def action(self, timestep: int) -> None:
        logging.debug(f"Timestep: {timestep}")
        if (timestep + 1) % 3:
            self.sense()
            self.senses += 1
        else:
            self.move()
            self.moves += 1

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

    def divide_board(self) -> None:
        """
        Divides board into four quandrants.
        """
        # Divide board for even D val
        if self.D % 2 == 0:
            for row, col in self.open_cells:
                if row in range(0, int((self.D/2))):
                    if col in range(0, int((self.D/2))):
                        self.q_1.add((row, col))
                    else:
                        self.q_2.add((row, col))
                else:
                    if col in range(0, int((self.D/2))):
                        self.q_3.add((row, col))
                    else:
                        self.q_4.add((row, col))
        # Divide board for odd D val
        else:
            for row in range(len(self.sensory_data)):
                for col in range(len(self.sensory_data)):
                    if row in range(0, floor(self.D/2)):
                        if col in range(floor(self.D/2), self.D):
                            self.q_2.add((row, col))
                    if row == floor(self.D/2) and col == floor(self.D/2):
                        self.q_2.add((row, col))
                    if row in range(0, floor((self.D/2)) + 1):
                        if col in range(0, floor((self.D/2))):
                            self.q_1.add((row, col))
                    if row in range(ceil(self.D/2), self.D):
                        if col in range(0, floor(self.D/2) + 1):
                            self.q_3.add((row, col))
                    if row in range(floor(self.D/2), self.D):
                        if col in range(ceil(self.D/2), self.D):
                            self.q_4.add((row, col))

    def plugged_leaks(self) -> bool:
        return self.leak_plugged
