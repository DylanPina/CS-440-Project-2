from game import GameBuilder
from config import Bots, init_logging
from ship import Seed

if __name__ == '__main__':
    init_logging()
    GameBuilder().add_ship(D=10, seed=None).add_bot(
        bot=Bots.BOT3, alpha=0.1).build().play(output_traversal=True)
    # Seed("input/seed.csv")
