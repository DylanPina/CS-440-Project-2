from game import GameBuilder
from config import Bots, init_logging
from ship.seeds import SingleSeed, MultiSeed

if __name__ == '__main__':
    init_logging()
    GameBuilder().add_ship(D=10, seed=None).add_bot(
        bot=Bots.BOT7, alpha=0.5).build().play(output_traversal=False)
    # SingleSeed("input/single_seed.csv")
    # MultiSeed("input/multi_seed.csv")
