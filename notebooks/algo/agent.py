from abc import ABC, abstractmethod
from typing import Tuple, List
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from notebooks.helpers import DATE_FMT, load_year_dataframe
from notebooks.algo.environment import EnvData


# product
# from itertools import product
# (buy amount, sale amount) pairs for currency
ACTIONS_F = (
    (100, 100),
    (100, 50),
    (100, 20),
    (100, 10),
    (100, 0),
    (50, 100),
    (50, 50),
    (50, 20),
    (50, 10),
    (50, 0),
    (20, 100),
    (20, 50),
    (20, 20),
    (20, 10),
    (20, 0),
    (10, 100),
    (10, 50),
    (10, 20),
    (10, 10),
    (10, 0),
    (0, 100),
    (0, 50),
    (0, 20),
    (0, 10),
    (0, 0),  # do nothing, day without trading
)
ACTIONS = (
    # (100, 100),
    (100, 0),
    (0, 100),
    (0, 0),
)

IDLE_ACTION_INDEX = len(ACTIONS) - 1
MAX_AMOUNT = 1000  # max amount of currency we are allowed to buy
wallet_step = 100
wallet_range = np.arange(0, MAX_AMOUNT+1, wallet_step)  # including upper bound
s_W = wallet_range.size  # space size for wallet discrete size

print('s_W', s_W)

class BaseAgent(ABC):
    """
    Agent is responsible for taking legit action
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    @property
    def actions_space_size(self) -> int:
        return len(ACTIONS)

    @property
    @abstractmethod
    def states_space_size(self) -> int:
        pass

    @abstractmethod
    def take_action(self, *args, **kwargs) -> int:
        pass

    @abstractmethod
    def to_state(self, *args, **kwargs) -> int:
        pass

    @abstractmethod
    def from_state(self, state: int):
        pass

    @abstractmethod
    def get_available_actions(self, state: int) -> List[int]:
        pass


class BaseTrader(BaseAgent):
    def __init__(self, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount_uah = amount
        self._starting_amount_uah = amount
        self.amount_usd = 0

    def trade(self, daily_data: EnvData):
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


class PolicyBasedTrader(BaseTrader):
    def __init__(self, policy, env, *args, **kwargs):
        super().__init__(amount=0, *args, **kwargs)
        self.policy = policy
        self.env = env

    def take_action(self, action: int, state: int, dry_run=False):
        # Assuming action is valid in a given state
        step, amount = self.from_state(state)

        daily_data = self.env.get_observation(step)
        rate_buy = daily_data.rate_buy
        rate_sale = daily_data.rate_sale

        d_buy, d_sale = ACTIONS[action]

        if self.verbose:
            print(f'#{step}: {rate_buy}/{rate_sale}')
        # do this in trade method
        usd_diff = d_buy - d_sale
        sale_uah = d_sale*rate_buy  # we will get this much uah
        buy_uah = d_buy*rate_sale  # we will pay this much uah
        uah_diff = sale_uah - buy_uah
        new_amount = amount + usd_diff  # currency amount
        if self.verbose:
            print(f'Taking action #{action}: ({d_buy}, {d_sale})')
        if not dry_run:
            self.amount_usd = new_amount
            self.amount_uah += uah_diff
            if self.amount_usd < 0 or self.amount_usd > MAX_AMOUNT:
                raise RuntimeError(
                    f'Wrong action [{action}] was performed. '
                    f'Currency amount is {self.amount_usd:.2f}'
                )

        reward = 0  # only count reward in the end of episode
        if step+1 == self.env.size:
            # reward = self.profit
            new_state = None
        else:
            new_state = self.to_state(step+1, new_amount)

        reward = uah_diff  # raw operation profit in uah
        if self.verbose:
            print(f'Reward = {reward}')
            print(f'Internal state: '
                  f'uah={self.amount_uah}; usd={self.amount_usd}\n')

        return reward, new_state

    def to_state(self, step: int, amount: int):
        assert amount % wallet_step == 0
        return step * s_W + amount // wallet_step

    def from_state(self, state: int) -> Tuple[int, int]:
        step = state // s_W
        amount = wallet_step * (state % s_W)
        return step, amount

    def get_available_actions(self, state: int) -> List[int]:
        actions = []
        # state.amount should be equal to self.amount_usd
        _, amount = self.from_state(state)
        for a, (d_buy, d_sale) in enumerate(ACTIONS):
            diff = d_buy - d_sale
            new_amount = amount + diff
            if 0 <= new_amount <= MAX_AMOUNT:
                actions.append(a)
        return actions

    @property
    def states_space_size(self) -> int:
        return self.env.size * s_W


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
        daily_data = EnvData(
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
