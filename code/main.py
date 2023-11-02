from game import GameBuilder
from config import Bots
from ship import Seed

if __name__ == '__main__':
    game = GameBuilder().add_ship(D=50, seed=None).add_bot(
        bot=Bots.BOT1, k=1).build().play(output_traversal=True)
