import logging
import time
from ship import Ship
from config import INITIAL_SHIP_LAYOUT_OUTPUT_FILE, SHIP_LAYOUT_TRAVERSAL_OUTPUT_FILE
from bots import Bot
from ship import print_layout
from .game_result import GameResult


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

        leaks_found = False
        timestep = 0
        start_time = time.time()
        while timestep < 100000:
            self.bot.action(timestep)
            if self.bot.plugged_leaks():
                self.bot.print_stats(timestep + 1)
                leaks_found = True
                break
            timestep += 1

        total_run_time = (start_time - time.time()) * 1000
        if not leaks_found:
            logging.info(
                f"Bot was not able to find the leak(s) in: {timestep} timesteps")
        logging.info(f"Finished in: {total_run_time} ms\n")

        if output_traversal:
            print_layout(
                self.bot.get_traversal(),
                file=SHIP_LAYOUT_TRAVERSAL_OUTPUT_FILE,
                bot_start_location=self.bot.starting_location,
                title="--Traversal--"
            )

        return GameResult(
            actions=timestep + 1,
            bot_variant=self.bot.variant,
            ship_dimensions=self.ship.D,
            run_time_ms=total_run_time
        )

    def bot_found_leak(self) -> bool:
        return self.bot.bot_location == self.ship.leak_location
