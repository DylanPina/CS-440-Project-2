from game import GameBuilder
from config import Bots, init_logging
from ship import Seed

if __name__ == '__main__':
    init_logging()
    GameBuilder().add_ship(D=5, seed=Seed("input/single_leak_seed.csv")).add_bot(
        bot=Bots.BOT1, k=1).build().play(output_traversal=False)
    # Seed("input/single_leak_seed.csv")
    # Seed("input/multi_leak_seed.csv", multi_leaks=True)
