from game import GameBuilder
from config import Bots
from ship import Seed

if __name__ == '__main__':
    game = GameBuilder().add_ship(D=0, seed=Seed("input/seed.csv")).add_bot(
        bot=Bots.BOT1, k=1).build().play(output_traversal=True)
    # Seed("input/seed.csv")
