import argparse
import statistics
from datetime import datetime, timedelta

import pandas as pd

from tables import Table
from download_rates import DATE_FMT


class Transaction(object):
    def __init__(self, amount, rate_buy, rate_sale, date, verbose=True):
        self.amount = amount  # amount of currency we bought
        self.rate_buy = rate_buy  # rate when trading
        # selling rate when trading to calculate future profit
        self.rate_sale = rate_sale
        self.date = date
        self._sold = False
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def sale(self, rate_sale, dry_run=False):
        amount = self.amount * rate_sale
        if not dry_run:
            profit = amount - self.price  # what we gain
            self.log(
                'Selling {amount:.2f}({rate_buy:.2f}) at {rate_sale:.2f}; '
                'total: {total:.2f}; profit: {profit:.2f}'.format(
                    amount=self.amount,
                    rate_buy=self.rate_buy,
                    rate_sale=rate_sale,
                    total=amount,
                    profit=profit,
                )
            )
            self._sold = True
        return amount

    @property
    def price(self):
        return self.amount * self.rate_buy

    @property
    def sold(self):
        return self._sold

    def __str__(self):
        return '{}: {:.2f} at {:.2f}'.format(
            self.date.strftime(DATE_FMT),
            self.amount,
            self.rate_buy
        )


class ShiftTrader(object):
    def __init__(self, starting_amount, shift, verbose=True):
        self.transactions = []  # history of all transactions
        self.amount = starting_amount  # operation money we use to buy currency
        self.shift = shift  # days we wait between buying/selling
        self._min_debt = 0
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
        # our perspective
        rate_sale = daily_data['buy']
        rate_buy = daily_data['sale']
        is_success = False  # if today's trade is successful
        for t in self.transactions:
            if (
                    t.date + timedelta(days=self.shift) == date and
                    rate_sale > t.rate_buy
            ):
                self.amount += t.sale(rate_sale)
                is_success = True

        # handle expired transactions
        expired_sold = self.handle_expired(date, rate_sale)

        if is_success or expired_sold:
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
        debt = self.amount - t.price
        # if debt < 0:
        #    raise ValueError(
        #       'Cannot buy {:.2f}$. Available: {:.2f}UAH'.format(self.daily_amount, self.amount))
        self._min_debt = min(debt, self._min_debt)

        self.amount -= t.price
        self.transactions.append(t)
        self.log('Amount in the end of the day: {:.2f}'.format(self.amount))

    def handle_expired(self, date, rate_sale):
        expired_sold = False  # any expired transaction was sold
        for t in self.transactions:
            if (
                    t.date + timedelta(days=self.shift) < date and
                    rate_sale > t.rate_buy and
                    not t.sold
            ):
                self.log('Selling expired {}'.format(t))
                self.amount += t.sale(rate_sale)
                expired_sold = True
        return expired_sold

    def close(self, rate_sale_closing):
        """Sell all hanging transaction for the rate specified"""
        self.log('Closing trading for {} transactions'.format(len(self.hanging)))
        for t in self.hanging:
            self.amount += t.sale(rate_sale_closing)

    @property
    def daily_amount(self):
        return 100

    def get_potential(self, rate_sale):
        return self.amount + sum([t.sale(rate_sale, dry_run=True)
                                  for t in self.hanging])

    @property
    def hanging(self):
        return list(filter(lambda t: not t.sold, self.transactions))


def launch_trading(*, year, starting_amount_uah, shift, verbose=True):
    """
    :param year: year we want to launch our algorithm on
    :param starting_amount_uah: how much we initially invest
    :param shift: days shift to wait before selling transaction
    :return:
    """
    currency = 'usd'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    ed = datetime.strptime('07.01.{}'.format(year), DATE_FMT)

    # Get end date
    # last_date_value = df.iloc[[-1]]['date'].item()
    # pd_date = pd.to_datetime(last_date_value)
    # ed = pd_date.to_pydatetime()

    print('Trading at period: [{} - {}]'.format(sd, ed))

    trader = ShiftTrader(
        starting_amount=starting_amount_uah,
        shift=shift,
        verbose=verbose,
    )

    i = 0

    s = {  # stats
        'year': year,
        'shift': shift,
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
    while current_date <= ed:  # until end date
        rate_sale = df.loc[df['date'] == current_date]['sale'].item()
        rate_buy = df.loc[df['date'] == current_date]['buy'].item()
        if verbose:
            print(
                '\n==>{}: {:.2f}/{:.2f}'.format(
                    current_date.strftime(DATE_FMT),
                    rate_buy,
                    rate_sale,
                )
            )

        daily_data = {
            'date': current_date,
            'buy': rate_sale,  # we buy currency, bank sale currency
            'sale': rate_buy,  # we sale currency, bank buy currency
        }
        potential = trader.get_potential(rate_buy)

        if verbose:
            print('Potential = {:.2f}'.format(potential))

        trader.trade(daily_data)
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

    s['hanging'] = len(trader.hanging)
    # close period at the last day no matter which rate
    # in order to calculate raw profit
    trader.close(rate_buy)

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
    print(
        '\n#### Report for {year} year. '
        'Shift: {shift} ####\n'.format(**stats)
    )
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
    print('Periods: {}'.format(len(stats['strikes'])))
    print('Success: {}'.format(len(stats['success'])))
    print('\tShortest: {}'.format(min(stats['success'])))
    print('\tLongest: {}'.format(max(stats['success'])))
    print('\tMean: {:.2f}'.format(statistics.mean(stats['success'])))
    print('Fail: {}'.format(len(stats['fail'])))
    print('\tShortest: {}'.format(min(stats['fail'])))
    print('\tLongest: {}'.format(max(stats['fail'])))
    print('\tMean: {:.2f}'.format(statistics.mean(stats['fail'])))

    print('\n#### Transactions ####\n')
    print('Total transactions: {}'.format(stats['transactions']))
    print('Hanging transactions: {}'.format(stats['hanging']))

    print('\n#### Profits ####\n')
    end_amount = stats['end_amount']
    print('Initial invested amount: {} UAH'.format(starting_amount))
    print('Amount we have in the end: {:.2f} UAH'.format(end_amount))
    print('Raw profit: {:.2f} UAH'.format(end_amount-starting_amount))
    print('Profit, %: {:.2f}'.format(end_amount / starting_amount * 100))


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
    parser = argparse.ArgumentParser(description='TradeAlgo#02v0')
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='which year you want to analyze',
    )
    parser.add_argument(
        '--shift',
        required=False,
        default=1,
        type=int,
        help='minimal delay between buying and selling',
    )
    parser.add_argument(
        '--amount',
        required=False,
        default=10000,
        type=int,
        help='amount of money you want to initially invest',
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    launch_trading(
        year=args.year,
        shift=args.shift,
        starting_amount_uah=args.amount,
    )

    # build_shift_comparison_table(year=args.year)
