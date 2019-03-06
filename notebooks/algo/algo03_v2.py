import os
import calendar
import operator
from concurrent import futures
from datetime import datetime

import neat
import tflearn
import numpy as np
import pandas as pd

from notebooks.helpers import DATE_FMT
from notebooks.algo import Transaction, DailyData
from notebooks.algo.agent import BaseTrader, evaluate_agent
from notebooks.algo.agent import IDLE_ACTION_INDEX, ACTIONS


INITIAL_AMOUNT = 20000


class NeatBasedTrader(BaseTrader):
    def __init__(self, net, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.net = net

    def take_action(
            self,
            *,
            amount_uah: float,
            amount_usd: int,
            daily_data: DailyData,
    ) -> int:
        rate_buy = daily_data.rate_buy
        rate_sale = daily_data.rate_sale

        input_data = [
            rate_buy,
            rate_sale,
            amount_uah,
            amount_usd,
            self.profit,
        ]
        output = self.net.activate(input_data)
        actions_order = np.flip(np.argsort(output))
        for i in actions_order:
            d_buy, d_sale = ACTIONS[i]
            price_sale = d_sale * rate_buy
            price_buy = d_buy * rate_sale
            if (
                d_sale <= amount_usd and
                price_buy <= (amount_uah + price_sale)
            ):
                return i


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        net = neat.nn.RecurrentNetwork.create(genome, config)
        trader = NeatBasedTrader(amount=INITIAL_AMOUNT, net=net)
        p, _ = evaluate_agent(agent=trader, verbose=False)
        genome.fitness = p


def run(config_file):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    p = neat.Population(config)
    # show_species_detail=True
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    p.add_reporter(neat.Checkpointer(10))

    epochs = 300
    winner = p.run(eval_genomes, epochs)
    print('\nBest genome:\n{!s}'.format(winner))

    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    trader = NeatBasedTrader(amount=INITIAL_AMOUNT, net=winner_net)
    print('\nTrade with best genome:')

    p, _ = evaluate_agent(agent=trader, verbose=True)
    print('\nProfit: {:.2f}'.format(p))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config')
    run(config_path)
