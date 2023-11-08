from game import Game
from ship import Ship
from bots.deterministic_bots import BotOne, BotTwo
from bots.probablistic_bots import BotThree, BotFour
from config import Bots
from ship import Seed


class GameBuilder():
    def __init__(self):
        self.game = Game()

    def add_bot(self, bot: Bots, k: int = None, alpha: int = None):
        match bot:
            case Bots.BOT1:
                self.game.set_bot(BotOne(k))
            case Bots.BOT2:
                self.game.set_bot(BotTwo(k))
            case Bots.BOT3:
                self.game.set_bot(BotThree(alpha))
            case Bots.BOT4:
                self.game.set_bot(BotFour(alpha))
        return self

    def add_ship(self, D: int, seed: Seed = None):
        self.game.set_ship(Ship(D, seed))
        return self

    def build(self):
        return self.game
