from game import Game
from ship import Ship
from bots.deterministic_bots import BotOne, BotTwo
from config import Bots
from ship import Seed


class GameBuilder():
    def __init__(self):
        self.game = Game()

    def add_bot(self, bot: Bots, k: int):
        match bot:
            case Bots.BOT1:
                self.game.set_bot(BotOne(k))
            case Bots.BOT2:
                self.game.set_bot(BotTwo(k))
        return self

    def add_ship(self, D: int = 50, seed: Seed = None):
        self.game.set_ship(Ship(D, seed))
        return self

    def build(self):
        return self.game
