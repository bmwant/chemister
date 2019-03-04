import random
import calendar
import operator
from concurrent import futures
from datetime import datetime

import tqdm
import pandas as pd

from notebooks.helpers import DATE_FMT
from notebooks.algo import Transaction, DailyData
from notebooks.algo.agent import BaseAgent, evaluate_agent

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

MAX_WORKERS = 50  # number of threads to evaluate agents in parallel


class RandomActionTrader(BaseAgent):
    def __init__(self, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount_uah = amount
        self._starting_amount_uah = amount
        self.amount_usd = 0

    def take_action(self, *, amount_uah, amount_usd, daily_data) -> int:
        rate_buy = daily_data.rate_buy
        rate_sale = daily_data.rate_sale

        # choose random action until it's valid
        total_tries = len(ACTIONS) * 2
        for _ in range(total_tries):
            action_num = random.randrange(len(ACTIONS))
            buy_amount, sale_amount = ACTIONS[action_num]
            price_sale = sale_amount * rate_buy
            price_buy = buy_amount * rate_sale
            if (
                    sale_amount <= amount_usd and
                    price_buy <= (amount_uah + price_sale)
            ):
                return action_num

        # just do nothing
        return len(ACTIONS) - 1

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
                    'Selling {amount_sale}$ at {rate:.2f} = {price:.2f}'.format(
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
                    'Buying {amount_buy}$ at {rate:.2f} = {price:.2f}'.format(
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


def main():
    year = 2018
    from pprint import pprint

    # epochs = 10
    # results = []
    # for _ in tqdm.tqdm(range(epochs)):
    #     r = evaluate_agent(agent=agent, verbose=False)
    #     results.append(r)
    #
    # top_n = sorted(results, reverse=True)[:100]
    # pprint(top_n)

    months = 12
    epochs = 5000
    # We can use a with statement to ensure threads are cleaned up promptly
    params = []
    with futures.ThreadPoolExecutor(max_workers=months) as executor:
        # Start the load operations and mark each future with its URL
        tasks = []
        for month in range(1, months+1):
            # Create agent for each process
            start_date = datetime.strptime(
                '01.{:02d}.{}'.format(month, year), DATE_FMT)
            end_day = calendar.monthrange(year, month)[1]
            end_date = datetime.strptime(
                '{}.{:02d}.{}'.format(end_day, month, year), DATE_FMT)

            params.append(dict(
                agent_factory=create_agent,
                start_date=start_date,
                end_date=end_date,
                epochs=epochs,
                n=month-1,
            ))
            # tasks.append(fut)

        results = list(executor.map(wrapper, params))
        for r in results:
            write_threshold_results(r, -400)

    print('\nDone!')


def wrapper(p):
    return get_best_results_for_period(**p)


def create_agent():
    return RandomActionTrader(amount=10000, verbose=False)


def write_threshold_results(trade_results, lower_threshold=-1000):
    df_data = []
    for profit, history in trade_results:
        if profit > lower_threshold:
            print('\nWriting trade actions for result: {:.2f}'.format(profit))
            df_data.extend(history)

    if df_data:
        df = pd.DataFrame(df_data)
        with open('random_trade_best_data.csv', 'a') as f:
            df.to_csv(f, index=False, header=False)


def get_best_results_for_period(
    agent_factory,
    start_date,
    end_date,
    epochs=100,
    top_n=10,
    n=1,
    max_workers=MAX_WORKERS,
):
    results = []

    progress = tqdm.tqdm(
        desc='#{:02d}'.format(n),
        total=epochs,
        position=n,
        leave=False,
        ascii=True,
    )
    tasks = []
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:

        for _ in range(epochs):
            agent = agent_factory()
            fut = executor.submit(
                evaluate_agent,
                agent=agent,
                start_date=start_date,
                end_date=end_date,
                verbose=False,
            )
            tasks.append(fut)

        for future in futures.as_completed(tasks):
            try:
                r = future.result()
                progress.update()
            except Exception as e:
                print('Exception occurred: %s' % e)
            else:
                results.append(r)

    progress.close()
    return sorted(results, key=operator.itemgetter(0), reverse=True)[:top_n]


if __name__ == '__main__':
    main()
