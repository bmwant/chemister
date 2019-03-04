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


def get_data():
    num_actions = len(ACTIONS)
    df = pd.read_csv('hindsight_trade_best_data.csv', header=None)
    X = df.loc[:,0:4].to_numpy()  # select first 5 rows
    actions = df.iloc[:,-1]  # select last row
    # convert actions to softmax format
    y = np.zeros((len(actions), num_actions))
    y[np.arange(len(actions)), actions] = 1
    return X, y


class NeatBasedTrader(BaseTrader):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    def take_action(self, *, amount_uah, amount_usd, daily_data) -> int:
        rate_buy = daily_data.rate_buy
        rate_sale = daily_data.rate_sale

        input_data = np.array([[
            rate_buy,
            rate_sale,
            amount_uah,
            amount_usd,
            self.profit,
        ]])
        prediction = self.model.predict(input_data)
        actions_order = np.flip(np.argsort(prediction))
        for i in actions_order[0]:
            # todo: do something, do not idle
            if i == IDLE_ACTION_INDEX:
                continue
            d_buy, d_sale = ACTIONS[i]
            price_sale = d_sale * rate_buy
            price_buy = d_buy * rate_sale
            if (
                d_sale <= amount_usd and
                price_buy <= (amount_uah + price_sale)
            ):
                return i

def eval_genomes():
    pass


def run(config_file):
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter())

    epochs = 300
    winner = p.run(eval_genomes, epochs)
    print('\nBest genome:\n{!s}'.format(winner))

    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    trader = NeatBasedTrader()
    print('\nTrade with best genome:')

    p, _ = evaluate_agent(agent=trader, verbose=True)
    print('\nProfit: {:.2f}'.format(p))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config')
    run(config_path)
