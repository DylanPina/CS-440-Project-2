from game import GameBuilder
from config import Bots, init_logging
from ship import Seed
from benchmark import BenchMarkTest

if __name__ == '__main__':
    init_logging()

    # single_seed = Seed("input/single_leak_seed.csv")
    # multi_seed = Seed("input/multi_leak_seed.csv", multi_leaks=True)

    GameBuilder()\
        .add_ship(D=30, seed=None)\
        .add_bot(bot=Bots.BOT3, alpha=0.0)\
        .build()\
        .play(output_traversal=False)

    # BenchMarkTest(itr=1, d=20, bot=Bots.BOT3,
    #               alpha_range=[(0.0, 0.1), 0.005]).run()
