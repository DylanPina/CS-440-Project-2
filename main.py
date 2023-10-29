from game import GameBuilder
from config import Bots

if __name__ == '__main__':
    game = GameBuilder().add_ship().add_bot(
        Bots.BOT1).build().play(output_traversal=True)
