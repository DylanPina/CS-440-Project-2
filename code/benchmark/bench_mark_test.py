import logging
import statistics
import matplotlib.pyplot as plt
from config import Bots
from .benchmark_assessment import BenchmarkAssessment
from matplotlib.ticker import (MultipleLocator,
                               FormatStrFormatter)
from typing import Tuple


class BenchMarkTest():

    def __init__(
            self,
            itr: int,
            d: int,
            bot: Bots,
            k_range: Tuple[Tuple[int, int], int] = None,
            alpha_range: Tuple[Tuple[float, float], float] = None
    ):
        self.itr = itr
        self.d = d
        self.bot = bot
        self.k_range = k_range
        self.alpha_range = alpha_range

    def run(self) -> None:
        if self.k_range:
            self.run_deterministic_bot()
        elif self.alpha_range:
            self.run_probabilistic_bot()
        else:
            logging.error("[BENCHMARK]: No range provided for bench mark test")
            exit(1)

    def run_deterministic_bot(self):
        actions_axis = []
        (k_start, k_end), k_step = self.k_range

        k_values = []
        k = k_start
        while k <= k_end:
            benchmark = BenchmarkAssessment(
                iterations=self.itr, bot_variant=self.bot, d=self.d, k=k).run()
            actions_list = []
            for game_result in benchmark:
                actions_list.append(game_result.actions)

            actions_axis.append(statistics.mean(actions_list))
            k_values.append(k)
            k += k_step

        _, axis = plt.subplots()

        axis.set_title(
            f"{self.bot} - {self.itr} for each k value; Ship size {self.d}x{self.d}")
        axis.set_ylabel('Actions')
        axis.set_xlabel('k')

        axis.xaxis.set_major_locator(MultipleLocator(1))
        axis.xaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))

        axis.scatter(k_values, actions_axis)
        plt.savefig(
            f"benchmark/graphs/{self.bot}-ITR({self.itr})D({self.d})")
        plt.clf()

    def run_probabilistic_bot(self):
        actions_axis = []
        (alpha_start, alpha_end), alpha_step = self.alpha_range

        alpha_values = []
        alpha = alpha_start
        while alpha <= alpha_end:
            benchmark = BenchmarkAssessment(
                iterations=self.itr, bot_variant=self.bot, d=self.d, alpha=alpha).run()
            actions_list = []
            for game_result in benchmark:
                actions_list.append(game_result.actions)

            actions_axis.append(statistics.mean(actions_list))
            alpha_values.append(alpha)
            alpha += alpha_step

        _, axis = plt.subplots()

        axis.set_title(
            f"{self.bot} - {self.itr} for each alpha value; Ship size {self.d}x{self.d}")
        axis.set_ylabel('Actions')
        axis.set_xlabel('alpha')

        axis.xaxis.set_major_locator(MultipleLocator(1))
        axis.xaxis.set_major_formatter(FormatStrFormatter('% 1.2f'))

        axis.scatter(alpha_values, actions_axis)
        plt.savefig(
            f"benchmark/graphs/{self.bot}-ITR({self.itr})D({self.d})")
        plt.clf()
