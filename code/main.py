import time
from game import GameBuilder
from config import Bots, init_logging
from ship import Seed
from benchmark import BenchMarkTest

if __name__ == '__main__':
    init_logging()

    # single_seed = Seed("input/single_leak_seed.csv")
    # multi_seed = Seed("input/multi_leak_seed.csv", multi_leaks=True)

    start_time = time.time()
    GameBuilder()\
        .add_ship(D=20, seed=None)\
        .add_bot(bot=Bots.BOT7, alpha=0.05)\
        .build()\
        .play(output_traversal=False)
    print("--- %s seconds ---" % (time.time() - start_time))

    # BenchMarkTest(itr=30, d=20, bot=Bots.BOT9, alpha_range=[
    #               (0.01, 0.11), 0.005], file_name=None).run()
