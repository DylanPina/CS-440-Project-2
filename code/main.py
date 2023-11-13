from game import GameBuilder
from config import Bots, init_logging
from ship import Seed
from benchmark import BenchMarkTest

if __name__ == '__main__':
    init_logging()

    # single_seed = Seed("input/single_leak_seed.csv")
    # multi_seed = Seed("input/multi_leak_seed.csv", multi_leaks=True)

    # GameBuilder()\
    #     .add_ship(D=10, seed=single_seed)\
    #     .add_bot(bot=Bots.BOT1, k=7)\
    #     .build()\
    #     .play(output_traversal=False)

    BenchMarkTest(itr=10, d=10, bot=Bots.BOT1, k_range=[(1, 5), 1]).run()
