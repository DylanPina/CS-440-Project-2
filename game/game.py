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

        if output_traversal:
            open(SHIP_LAYOUT_OUTPUT, "w").close()
            print_layout(self.ship.layout, title="--Initial State--")
