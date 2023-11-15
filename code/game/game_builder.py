from game import Game
from ship import Ship
from bots.deterministic_bots import BotOne, BotTwo, BotFive, BotSix
from bots.probablistic_bots import BotThree, BotFour, BotSeven
from bots.probablistic_bots.multiple_leaks import BotEight, BotNine
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
            case Bots.BOT5:
                self.game.set_bot(BotFive(k))
            case Bots.BOT6:
                self.game.set_bot(BotSix(k))
            case Bots.BOT7:
                self.game.set_bot(BotSeven(alpha))
            case Bots.BOT8:
                self.game.set_bot(BotEight(alpha))
            case Bots.BOT9:
                self.game.set_bot(BotNine(alpha))
        return self

    def add_ship(self, D: int, seed: Seed = None):
        self.game.set_ship(Ship(D, seed))
        return self

    def build(self):
        return self.game
