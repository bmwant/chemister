import argparse
import statistics
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from download_rates import DATE_FMT


def build_chart(data, currency, title=''):
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.canvas.set_window_title('Success/fail periods chart')
    index = np.arange(len(data))
    success_data = [e if e > 0 else 0 for e in data]
    fail_data = [e if e < 0 else 0 for e in data]
    plt.bar(index, success_data, color='g', zorder=3, label='success')
    plt.bar(index, fail_data, color='r', zorder=3, label='fail')
    plt.yticks(np.arange(min(data), max(data), step=30))

    ax.hlines(y=0, xmin=-1, xmax=len(data), linewidth=1, color='k', zorder=4)
    ax.yaxis.grid(True, zorder=0)
    ax.legend()
    plt.title(title)
    plt.show()


def count_periods(df, year, shift=1):
    success = 0
    fail = 0
    skipped = 0
    i = 0  # total iterations
    strike = 0  # length of a period (either success or fail)
    flag = False  # whether we incrementing same period
    total_diff = 0  # gross sale/buy diff
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    ed = datetime.strptime('31.12.{}'.format(year), DATE_FMT)
    current_date = sd
    data = []
    inc = []
    dec = []
    stats = {}
    while current_date <= ed:
        date_buy = current_date - timedelta(days=shift)
        # we sale currency, bank buy currency
        rate_sale = df.loc[df['date'] == current_date]['buy'].item()

        if date_buy >= sd:
            # we buy currency, bank sale currency
            rate_buy = df.loc[df['date'] == date_buy]['sale'].item()
            if rate_sale > rate_buy:
                if flag is True:
                    strike += 1
                else:
                    flag = True
                    if strike:
                        data.append(-strike)
                        dec.append(strike)
                    print('+ start at {}'.format(current_date))
                    # print('- {}'.format(strike))
                    strike = 1
                success += 1
            else:
                if flag is False:
                    strike += 1
                else:
                    flag = False
                    print('+ end at {}'.format(current_date))
                    # print('+ {}'.format(strike))
                    inc.append(strike)
                    data.append(strike)
                    strike = 1
                fail += 1
        else:
            skipped += 1
        i += 1
        current_date += timedelta(days=1)

    if flag is True:
        inc.append(strike)
        data.append(strike)
    else:
        dec.append(strike)
        data.append(-strike)

    print('Stats for shift {}'.format(shift))
    print('Total inc/dec: {}/{}'.format(sum(inc), sum(dec)))
    print('\tSuccess {}'.format(success))
    print('\tFail {}'.format(fail))
    print('\tSkipped: {}'.format(skipped))
    print('\tTotal periods: {}'.format(len(data)))
    print('\tShortest/longest +strike: {}/{}'.format(min(inc), max(inc)))
    print('\tShortest/longest -strike: {}/{}'.format(min(dec), max(dec)))
    print('\tMean +strike: {:.2f}'.format(statistics.mean(inc)))
    print('\tMedian +strike: {:.2f}'.format(statistics.median(inc)))
    try:
        print('\tMode +strike: {}'.format(statistics.mode(inc)))
    except statistics.StatisticsError:
        print('\tNo mode for +strike')
    print('\tMean -strike: {:.2f}'.format(statistics.mean(dec)))
    print('\tMedian -strike: {:.2f}'.format(statistics.median(dec)))
    try:
        print('\tMode -strike: {}'.format(statistics.mode(dec)))
    except statistics.StatisticsError:
        print('\tNo mode for -strike')

    return data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='which year you want to analyze',
    )
    args = parser.parse_args()
    return args


def main(year):
    print('Showing stats for {} year'.format(year))
    currency = 'usd'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)

    # for s in range(31):
    #     shift = s + 1
    #     count_for_shift(df, year, shift)

    shifts = [8]
    for shift in shifts:
        data = count_periods(df, year, shift)
        title = 'Transactions for shift={}'.format(shift)
        # build_chart(shifted_df, currency, title, show_profit=True)
        build_chart(data, currency, title)


if __name__ == '__main__':
    args = parse_args()
    main(year=args.year)
