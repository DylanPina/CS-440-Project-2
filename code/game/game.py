import logging
import time
from ship import Ship
from config import INITIAL_SHIP_LAYOUT_OUTPUT_FILE, SHIP_LAYOUT_TRAVERSAL_OUTPUT_FILE
from bots import Bot
from ship import print_layout


class Game:
    def __init__(self):
        self.ship = None
        self.bot = None

    def set_ship(self, ship: Ship) -> None:
        self.ship = ship

    def set_bot(self, bot: Bot) -> None:
        self.bot = bot

    def play(self, output_traversal: bool = False) -> None:
        if not self.ship:
            logging.error("Cannot play game without ship!")
            exit(1)
        if not self.bot:
            logging.error("Cannot play game without bot!")
            exit(1)

        self.ship.add_bot(self.bot)
        self.ship.place_leak()

        print_layout(
            self.ship.layout, file=INITIAL_SHIP_LAYOUT_OUTPUT_FILE, title="--Initial State--")

        start_time = time.time()
        timestep = 0
        while timestep < 100000:
            self.bot.action(timestep)
            if self.bot_found_leak():
                logging.info(f"Bot found the leak in {timestep} timesteps!")
                break
            timestep += 1

        logging.info(f"Finished in: {(time.time() - start_time) * 1000} ms")

        if output_traversal: 
            print_layout(
                self.bot.get_traversal(),
                file=SHIP_LAYOUT_TRAVERSAL_OUTPUT_FILE,
                bot_start_location=self.bot.starting_location,
                title="--Traversal--"
            )

    def bot_found_leak(self) -> bool:
        return self.bot.bot_location == self.ship.leak_location
