from game import GameBuilder
from config import Bots, init_logging
from ship import Seed
from benchmark import BenchMarkTest

if __name__ == '__main__':
    init_logging()

    # single_seed = Seed("input/single_leak_seed.csv")
    multi_seed = Seed("input/multi_leak_seed.csv", multi_leaks=True)

    # GameBuilder()\
    #     .add_ship(D=20, seed=multi_seed)\
    #     .add_bot(bot=Bots.BOT6, k=4.5)\
    #     .build()\
    #     .play(output_traversal=False)

    BenchMarkTest(itr=10, d=20, bot=Bots.BOT5,
                  k_range=[(1, 10), 0.5]).run()
