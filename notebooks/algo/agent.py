from abc import ABC, abstractmethod
from typing import Tuple, List
from datetime import datetime, timedelta

import pandas as pd

from notebooks.helpers import DATE_FMT, load_year_dataframe
from . import DailyData


# product
# from itertools import product
# (buy amount, sale amount) pairs for currency
ACTIONS = (
    (100, 100),
    (100, 50),
    (100, 20),
    (100, 0),
    (50, 100),
    (50, 50),
    (50, 20),
    (50, 0),
    (20, 100),
    (20, 50),
    (20, 20),
    (20, 0),
    (0, 100),
    (0, 50),
    (0, 20),
    (0, 0),  # do nothing, day without trading
)

IDLE_ACTION_INDEX = len(ACTIONS) - 1


class BaseAgent(ABC):
    def __init__(self, verbose=False):
        self.verbose = verbose

    @abstractmethod
    def take_action(self, *args, **kwargs) -> int:
        pass


class BaseTrader(BaseAgent):
    def __init__(self, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount_uah = amount
        self._starting_amount_uah = amount
        self.amount_usd = 0

    def trade(self, daily_data):
        action_num = self.take_action(
            amount_uah=self.amount_uah,
            amount_usd=self.amount_usd,
            daily_data=daily_data,
        )
        d_buy, d_sale = ACTIONS[action_num]

        rate_buy = daily_data.rate_buy
        rate_sale = daily_data.rate_sale

        # Collect train data
        data_row = (
            rate_buy,
            rate_sale,
            self.amount_uah,
            self.amount_usd,
            self.profit,
            action_num,
        )

        if d_sale:
            # We are selling some currency
            price_sale = d_sale * rate_buy
            self.amount_uah += price_sale
            self.amount_usd -= d_sale
            assert self.amount_usd >= 0
            if self.verbose:
                print(
                    '>>> Selling {amount_sale}$ at {rate:.2f} '
                    '= {price:.2f}'.format(
                        amount_sale=d_sale,
                        rate=rate_buy,
                        price=price_sale,
                    )
                )

        if d_buy:
            # We are buying some currency
            price_buy = d_buy * rate_sale
            self.amount_uah -= price_buy
            self.amount_usd += d_buy
            assert self.amount_uah >= 0
            if self.verbose:
                print(
                    '<<< Buying {amount_buy}$ at {rate:.2f} '
                    '= {price:.2f}'.format(
                        amount_buy=d_buy,
                        rate=rate_sale,
                        price=price_buy,
                    )
                )

        if not (d_buy or d_sale) and self.verbose:
            print('Idling...')

        return data_row

    @property
    def profit(self) -> float:
        return self.amount_uah - self._starting_amount_uah


# todo: reuse launch_trading
def evaluate_agent(
    agent: BaseTrader,
    start_date=None,
    end_date=None,
    verbose=False,
) -> Tuple[float, List]:
    year = 2018
    currency = 'usd'
    df = load_year_dataframe(year=year, currency=currency)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)
    sd = start_date or datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    ed = end_date or datetime.strptime('31.12.{}'.format(year), DATE_FMT)

    if verbose:
        print('Evaluating on period: [{} - {}]'.format(
            sd.strftime(DATE_FMT), ed.strftime(DATE_FMT),
        ))

    step = 0
    history = []  # history of daily data and corresponding actions
    current_date = sd  # starting date
    while current_date <= ed:  # until end date
        rate_buy = df.loc[df['date'] == current_date]['buy'].item()
        rate_sale = df.loc[df['date'] == current_date]['sale'].item()
        daily_data = DailyData(
            day=step,
            rate_buy=rate_buy,
            rate_sale=rate_sale,
        )
        if verbose:
            print(daily_data)

        h = agent.trade(daily_data=daily_data)
        history.append(h)

        if verbose:
            print('Current profit: {:.2f}\n'.format(agent.profit))

        current_date += timedelta(days=1)
        step += 1

    if verbose:
        print('End state: {:.2f}USD and {:.2f}UAH'.format(
            agent.amount_usd, agent.amount_uah,
        ))
    return agent.profit, history
