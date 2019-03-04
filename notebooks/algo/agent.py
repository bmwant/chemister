from datetime import datetime, timedelta
from abc import ABC, abstractmethod

import pandas as pd

from notebooks.helpers import DATE_FMT, load_year_dataframe
from . import DailyData


class BaseAgent(ABC):
    def __init__(self, verbose=False):
        self.verbose = verbose

    @abstractmethod
    def take_action(self, *args, **kwargs) -> int:
        pass


# todo: reuse launch_trading
def evaluate_agent(
    agent,
    start_date=None,
    end_date=None,
    verbose=False,
) -> float:
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

        agent.trade(daily_data=daily_data)

        if verbose:
            print('Current profit: {:.2f}\n'.format(agent.profit))

        current_date += timedelta(days=1)
        step += 1

    if verbose:
        print('End state: {:.2f}USD and {:.2f}UAH'.format(
            agent.amount_usd, agent.amount_uah,
        ))
    return agent.profit
