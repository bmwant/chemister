import random
import calendar
import operator
from concurrent import futures
from datetime import datetime

import tqdm
import pandas as pd

from notebooks.helpers import DATE_FMT
from notebooks.algo import Transaction, DailyData
from notebooks.algo.agent import BaseTrader, evaluate_agent
from notebooks.algo.agent import IDLE_ACTION_INDEX, ACTIONS


MAX_WORKERS = 50  # number of threads to evaluate agents in parallel


class RandomActionTrader(BaseTrader):
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


class HindsightTrader(BaseTrader):
    def take_action(self, *, amount_uah, amount_usd, daily_data) -> int:
        rate_buy = daily_data.rate_buy
        rate_sale = daily_data.rate_sale

        if rate_sale >= 27.7:
            return IDLE_ACTION_INDEX

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
    epochs = 1000
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
            write_threshold_results(r, -200)

    print('\nDone!')


def wrapper(p):
    return get_best_results_for_period(**p)


def create_agent():
    return HindsightTrader(amount=10000, verbose=False)


def write_threshold_results(trade_results, lower_threshold=-1000):
    df_data = []
    for profit, history in trade_results:
        if profit > lower_threshold:
            print('\nWriting trade actions for result: {:.2f}'.format(profit))
            df_data.extend(history)

    if df_data:
        df = pd.DataFrame(df_data)
        with open('hindsight_trade_best_data.csv', 'a') as f:
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
