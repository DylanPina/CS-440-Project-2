import logging
from .probabilistic_bot import ProbabilisticBot
from config import Bots


class BotFour(ProbabilisticBot):
    """
    Similar to bot 3 in regards to having a probabilistic leak detector and how it proceeds to find the leak. However, this bot will wait two timesteps of sensing before moving inorder to collect more data about its surroundings before constructing a path to the cell with the highest probability. By this adjustment, the bot will have more information before it starts traversing down a path and is less likely to waste time going down the wrong path.
    """

    def __init__(self, alpha: int) -> None:
        super().__init__(alpha)
        self.variant = Bots.BOT4

        logging.info(f"Bot variant: {self.variant}")
        logging.info(f"Alpha: {self.alpha}")

    def action(self, timestep: int) -> None:
        logging.debug(f"Timestep: {timestep}")
        if (timestep + 1) % 3:
            self.sense()
            self.senses += 1
        else:
            self.move()
            self.moves += 1
