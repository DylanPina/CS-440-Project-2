from game import GameBuilder
from config import Bots, init_logging
from ship import Seed
from benchmark import BenchMarkTest

if __name__ == '__main__':
    init_logging()

    # single_seed = Seed("input/single_leak_seed.csv")
    # multi_seed = Seed("input/multi_leak_seed.csv", multi_leaks=True)

    # GameBuilder()\
    #     .add_ship(D=10, seed=None)\
    #     .add_bot(bot=Bots.BOT1, k=5)\
    #     .build()\
    #     .play(output_traversal=False)

    BenchMarkTest(itr=30, d=30, bot=Bots.BOT1, k_range=[(1, 10), 1]).run()
