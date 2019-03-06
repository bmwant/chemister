import argparse
from datetime import datetime, timedelta

import pandas as pd

from notebooks.build_chart import build_chart
from notebooks.helpers import DATE_FMT, load_year_dataframe


def count_for_shift(df, year, shift=1):
    success = 0
    fail = 0
    skipped = 0
    i = 0  # total iterations
    total_diff = 0  # gross sale/buy diff
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    ed = datetime.strptime('31.12.{}'.format(year), DATE_FMT)
    current_date = sd
    data = []
    while current_date <= ed:
        date_buy = current_date - timedelta(days=shift)
        # we sale currency, bank buy currency
        rate_sale = df.loc[df['date'] == current_date]['buy'].item()

        if date_buy >= sd:
            # we buy currency, bank sale currency
            rate_buy = df.loc[df['date'] == date_buy]['sale'].item()
            if rate_sale > rate_buy:
                total_diff += rate_sale - rate_buy
                success += 1
            else:
                fail += 1
            data.append([current_date, rate_buy, rate_sale])
        else:
            skipped += 1
        i += 1
        current_date += timedelta(days=1)

    print('Stats for shift {}'.format(shift))
    print('\tSuccess {}'.format(success))
    print('\tFail {}'.format(fail))
    print('\tSkipped: {}'.format(skipped))
    print('\tTotal: {}'.format(i))
    print('\tTotal diff: {:.2f}'.format(total_diff))
    return data


def count_unprofitable_days(df, year):
    i = 0  # total iterations
    total_diff = 0  # gross sale/buy diff
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    ed = datetime.strptime('31.12.{}'.format(year), DATE_FMT)
    current_date = sd
    data = []
    success = 0
    t_success = 0  # threshold success days
    threshold = 0.25
    fail = 0
    min_rate = float('inf')
    min_sale_rate = df['sale'].min()  # buy as much as possible at this ))
    max_buy_rate = df['buy'].max()  # anyway min_rate should be lower
    while current_date <= ed:
        rate_buy = df.loc[df['date'] == current_date]['buy'].item()
        rate_sale = df.loc[df['date'] == current_date]['sale'].item()

        d = df.loc[
            (df['date'] > current_date) & (df['buy'] > rate_sale)
        ]
        if len(d.index):
            success += 1
        else:
            fail += 1
            min_rate = min(min_rate, rate_sale)

        t_d = df.loc[
            (df['date'] > current_date) & (df['buy'] >= rate_sale + threshold)
        ]
        if len(t_d.index):
            t_success += 1

        i += 1
        current_date += timedelta(days=1)

    print('Profitable days in {} year'.format(year))
    print('\tSuccess {}'.format(success))
    print('\tSuccess with threshold of {}: {}'.format(threshold, t_success))
    print('\tFail {}'.format(fail))
    print('\tTotal: {}'.format(i))
    print('\tDo not buy above {:.2f}'.format(min_rate))
    # print('\tTotal diff: {:.2f}'.format(total_diff))


def parse_args():
    parser = argparse.ArgumentParser(description='Count shifts for a year')
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='which year you want to analyze',
    )
    args = parser.parse_args()
    return args


def main(year):
    currency = 'usd'
    df = load_year_dataframe(year=year, currency=currency)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)

    # for s in range(31):
    #     shift = s + 1
    #     count_for_shift(df, year, shift)

    # shifts = [8, 16, 28]
    # for shift in shifts:
    #     data = count_for_shift(df, year, shift)
    #     shifted_df = pd.DataFrame(
    #         columns=['date', 'buy', 'sale'],
    #         data=data,
    #     )
    #     title = 'Transactions for shift={}'.format(shift)
    #     build_chart(shifted_df, currency, title, show_profit=True)

    count_unprofitable_days(df, year=year)


if __name__ == '__main__':
    args = parse_args()
    main(year=args.year)
