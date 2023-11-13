from typing import List
from config import GameResult, Bots
from game import GameBuilder
from ship import Seed


class BenchmarkAssessment:
    def __init__(self, iterations: int, bot_variant: Bots, d: int, k: int = None, alpha: float = None):
        self.iterations = iterations
        self.bot_variant = bot_variant
        self.d = d
        self.k = k
        self.alpha = alpha
        self.results = []

    def run(self, output: bool = False, seed: Seed = None) -> List[GameResult]:
        benchmarks = []
        for _ in range(self.iterations):
            game = GameBuilder()\
                .add_ship(D=self.d, seed=seed)\
                .add_bot(bot=self.bot_variant, k=self.k, alpha=self.alpha)\
                .build()
            benchmarks.append(game.play(output))
        return benchmarks
