import logging
from .probabilistic_bot import ProbabilisticBot
from config import Bots


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
