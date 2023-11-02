from ship import Ship
from config import SHIP_LAYOUT_OUTPUT
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
            print("[ERROR]: Cannot play game without ship!")
            exit(1)
        if not self.bot:
            print("[ERROR]: Cannot play game without bot!")
            exit(1)

        self.ship.add_bot(self.bot)
        self.ship.place_leak()

        open(SHIP_LAYOUT_OUTPUT, "w").close()
        print_layout(self.ship.layout, title="--Initial State--")

        timestep = 0
        while timestep < 10000:
            if timestep % 2 == 0:
                self.bot.sense()
            elif timestep % 2 == 1:
                self.bot.move()
                print(f"[INFO]: New location {self.bot.bot_location}")
                if self.bot_found_leak():
                    print(f"[SUCCESS]: Bot found the leak in {timestep} timesteps!")
                    break

            timestep += 1

        if output_traversal:
            print_layout(
                self.bot.get_traversal(),
                bot_start_location=self.bot.starting_location,
                title="--Traversal--",
            )

    def bot_found_leak(self) -> bool:
        return self.bot.bot_location == self.ship.leak_location
