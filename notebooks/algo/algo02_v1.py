import argparse
import statistics
from datetime import datetime, timedelta

import click
import pandas as pd

from notebooks.tables import Table
from notebooks.helpers import DATE_FMT
from notebooks.algo import Transaction


class ShiftTrader(object):
    def __init__(self, verbose=True):
        self.transactions = []  # history of all transactions
        self.amount = 0  # track fund
        self._min_debt = 0  # max negative delta of a fund
        self._success = []  # success periods
        self._fail = []  # fail periods
        self._strike_data = []
        self._strike = 0  # length of the period
        self._flag = False  # whether we incrementing same period
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def trade(self, daily_data):
        date = daily_data['date']
        # bank's perspective
        rate_buy = daily_data['buy']
        rate_sale = daily_data['sale']
        is_success = False  # if today's trade is successful
        for t in self.transactions:
            if (
                    t.date <  date and
                    rate_buy - t.rate_sale > 0 and
                    not t.sold
            ):
                end_amount  = t.sale(rate_buy)
                self.amount += end_amount
                message = '<<< {}$ for {:.2f} = {:.2f} UAH'.format(
                    t.amount,
                    rate_buy,
                    end_amount,
                )
                click.secho(message, fg='green', bold=True)
                is_success = True

        if is_success:
            if self._flag is True:
                self._strike += 1
            else:
                self._flag = True
                if self._strike:
                    self._fail.append(self._strike)
                    self._strike_data.append(-self._strike)
                self._strike = 1

        else:
            if self._flag is False:
                self._strike += 1
            else:
                self._flag = False
                self._success.append(self._strike)
                self._strike_data.append(self._strike)
                self._strike = 1

        # buy some amount of currency
        t = Transaction(
            rate_buy=rate_buy,
            rate_sale=rate_sale,
            amount=self.daily_amount,
            date=date,
            verbose=self.verbose,
        )
        debt = self.amount - t.initial_price
        # Lowest amplitude
        self._min_debt = min(debt, self._min_debt)

        self.amount -= t.initial_price
        click.secho(
            '>>> {}$ for {:.2f} = {:.2f} UAH'.format(100, rate_sale, t.initial_price),
            fg='blue', bold=True)
        self.transactions.append(t)
        self.log('Amount in the end of the day: {:.2f}'.format(self.amount))

    def close(self, rate_buy_closing):
        """Sell all hanging transaction to the bank for the rate specified"""
        self.log(
            'Closing trading for {} transactions'.format(len(self.hanging)))
        for t in self.hanging:
            self.amount += t.sale(rate_buy_closing)

    @property
    def daily_amount(self):
        return 100

    def get_potential(self, rate_buy_today):
        """Suppose we sell all our transactions to the bank and today's rate"""
        return self.amount + sum([t.sale(rate_buy_today, dry_run=True)
                                  for t in self.hanging])

    @property
    def hanging(self):
        return list(filter(lambda t: not t.sold, self.transactions))


def launch_trading(*, year, verbose=True):
    currency = 'usd'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    # ed = datetime.strptime('01.02.{}'.format(year), DATE_FMT)

    # Get end date
    last_date_value = df.iloc[[-1]]['date'].item()
    pd_date = pd.to_datetime(last_date_value)
    ed = pd_date.to_pydatetime()

    print('Trading at period: [{} - {}]'.format(sd, ed))

    trader = ShiftTrader(verbose=verbose)

    i = 0
    starting_amount_uah = 0
    s = {  # stats
        'year': year,
        'k1_return': None,
        'k1_return_soft': None,
        'k5_return': None,
        'k5_return_soft': None,
        'p10_return': None,
        'p10_return_soft': None,
        'exit_period': None,
        # strikes
        'success': None,
        'fail': None,
        'strikes': None,
        'starting_amount': starting_amount_uah,
        'end_amount': None,
        'debt': None,
        # transactions
        'transactions': None,  # atomic bank operations
        'handing': None,  # transactions without profit
    }

    current_date = sd  # starting date
    rate_buy_closing = None
    while current_date <= ed:  # until end date
        rate_buy = df.loc[df['date'] == current_date]['buy'].item()
        rate_sale = df.loc[df['date'] == current_date]['sale'].item()
        if verbose:
            print(
                '\n==> {}: {:.2f}/{:.2f}'.format(
                    current_date.strftime(DATE_FMT),
                    rate_buy,
                    rate_sale,
                )
            )

        daily_data = {
            'date': current_date,
            'buy': rate_buy,  # we buy currency, bank sale currency
            'sale': rate_sale,  # we sale currency, bank buy currency
        }

        trader.trade(daily_data)

        potential = trader.get_potential(rate_buy)
        if verbose:
            print('Potential = {:.2f}'.format(potential))

        days_passed = current_date - sd  # how many days passed since start
        if s['exit_period'] is None and potential > starting_amount_uah:
            s['exit_period'] = days_passed
        if s['k1_return'] is None and trader.amount >= starting_amount_uah + 1000:
            s['k1_return'] = days_passed
        if s['k1_return_soft'] is None and potential >= starting_amount_uah + 1000:
            s['k1_return_soft'] = days_passed
        if s['k5_return'] is None and trader.amount >= starting_amount_uah + 5000:
            s['k5_return'] = days_passed
        if s['k5_return_soft'] is None and potential >= starting_amount_uah + 5000:
            s['k5_return_soft'] = days_passed
        if s['p10_return'] is None and trader.amount >= 1.1 * starting_amount_uah:
            s['p10_return'] = days_passed
        if s['p10_return_soft'] is None and potential >= 1.1 * starting_amount_uah:
            s['p10_return_soft'] = days_passed

        i += 1
        current_date += timedelta(days=1)
        rate_buy_closing = rate_buy

    s['hanging'] = len(trader.hanging)
    # close period at the last day no matter which rate
    # in order to calculate raw profit
    trader.close(rate_buy_closing)

    # sell every purchased transaction
    s['transactions'] = 2 * len(trader.transactions)
    s['strikes'] = trader._strike_data
    s['success'] = trader._success
    s['fail'] = trader._fail
    s['debt'] = trader._min_debt
    s['end_amount'] = trader.amount

    if verbose:
        print_stats(s)

    return s  # return statistics for trading period


def print_stats(stats):
    starting_amount = stats['starting_amount']
    debt = stats['debt']
    print('\n#### Report for {year} year ####\n'.format(year=stats['year']))
    print('Minimal investment needed: {:.2f} UAH'.format(starting_amount-debt))

    print('\n#### Return/exit periods ####\n')
    if stats['k1_return'] is not None:
        print('1K profit period: {} days'.format(stats['k1_return'].days))
    else:
        print('1K HARD is unreachable within given period')

    if stats['k1_return_soft'] is not None:
        print('1K gain soft period: {} days'.format(stats['k1_return_soft'].days))
    else:
        print('1K SOFT is unreachable within given period')

    if stats['k5_return'] is not None:
        print('5K profit period: {} days'.format(stats['k5_return'].days))
    else:
        print('5K HARD is unreachable within given period')

    if stats['k5_return_soft'] is not None:
        print('5K gain soft period: {} days'.format(stats['k5_return_soft'].days))
    else:
        print('5K SOFT is unreachable within given period')

    if stats['p10_return'] is not None:
        print('10% profit period: {} days'.format(stats['p10_return'].days))
    else:
        print('10% HARD is unreachable within given period')

    if stats['p10_return_soft'] is not None:
        print('10% gain soft period: {} days'.format(stats['p10_return_soft'].days))
    else:
        print('10% SOFT is unreachable within given period')

    if stats['exit_period'] is not None:
        print('Exit period: {} days\n'.format(stats['exit_period'].days))
    else:
        print('Cannot exit within given period\n')

    print('\n#### Strikes ####\n')
    success = stats['success']
    fail = stats['fail']
    print('Periods: {}'.format(len(stats['strikes'])))
    print('Success: {}'.format(len(success)))
    print('\tShortest: {}'.format(min(success) if success else 0))
    print('\tLongest: {}'.format(max(success) if success else 0))
    print('\tMean: {:.2f}'.format(statistics.mean(success) if success else 0))
    print('Fail: {}'.format(len(fail)))
    print('\tShortest: {}'.format(min(fail) if fail else 0))
    print('\tLongest: {}'.format(max(fail) if fail else 0))
    print('\tMean: {:.2f}'.format(statistics.mean(fail) if fail else 0))

    print('\n#### Transactions ####\n')
    print('Total transactions: {}'.format(stats['transactions']))
    print('Hanging transactions: {}'.format(stats['hanging']))

    print('\n#### Profits ####\n')
    end_amount = stats['end_amount']
    print('Initial invested amount: {} UAH'.format(starting_amount))
    print('Amount we have in the end: {:.2f} UAH'.format(end_amount))
    print('Raw profit: {:.2f} UAH'.format(end_amount-starting_amount))
    if starting_amount:
        print('Profit, %: {:.2f}'.format((end_amount / starting_amount * 100)))


def build_shift_comparison_table(year):
    header = [
        'year',
        'shift',
        'minimal investment',
        'raw profit, uah',
        'profit, %',
    ]
    data = []
    for s in range(0, 31):
        shift = s+1

        stats = launch_trading(
            year=year,
            shift=shift,
            starting_amount_uah=0,
            verbose=False,
        )
        min_investment = -stats['debt']
        row = [
            year,
            shift,
            '{:.2f}'.format(min_investment),
            '{:.2f}'.format(stats['end_amount']),
            '{:.2f}'.format(stats['end_amount'] / min_investment * 100),
        ]
        data.append(row)

    t = Table(header=header, data=data)
    t.print()


def parse_args():
    parser = argparse.ArgumentParser(description='TradeAlgo#02v1')
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='which year you want to analyze',
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    launch_trading(
        year=args.year,
    )

    # build_shift_comparison_table(year=args.year)
