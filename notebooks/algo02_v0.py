import argparse
from datetime import datetime, timedelta

import pandas as pd

from download_rates import DATE_FMT


class Transaction(object):
    def __init__(self, amount, rate_buy, rate_sale, date):
        self.amount = amount  # amount of currency we bought
        self.rate_buy = rate_buy  # rate when trading
        # selling rate when trading to calculate future profit
        self.rate_sale = rate_sale
        self.date = date
        self._sold = False

    def sale(self, rate_sale, dry_run=False):
        amount = self.amount * rate_sale
        if not dry_run:
            profit = amount - self.price  # what we gain
            print('Selling {amount:.2f}({rate_buy:.2f}) at {rate_sale:.2f}; '
                  'total: {total:.2f}; profit: {profit:.2f}'.format(
                amount=self.amount,
                rate_buy=self.rate_buy,
                rate_sale=rate_sale,
                total=amount,
                profit=profit,
            ))
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
    def __init__(self, starting_amount, shift):
        self.transactions = []  # history of all transactions
        self.amount = starting_amount  # operation money we use to buy currency
        self.shift = shift  # days we wait between buying/selling
        self._min_debt = 0

    def trade(self, daily_data):
        date = daily_data['date']
        # our perspective
        rate_sale = daily_data['buy']
        rate_buy = daily_data['sale']
        for t in self.transactions:
            if (
                    t.date + timedelta(days=self.shift) == date and
                    rate_sale > t.rate_buy
            ):
                self.amount += t.sale(rate_sale)

        # handle expired transactions
        self.handle_expired(date, rate_sale)

        # buy some amount of currency
        t = Transaction(
            rate_buy=rate_buy,
            rate_sale=rate_sale,
            amount=self.daily_amount,
            date=date,
        )
        debt = self.amount - t.price
        # if debt < 0:
        #    raise ValueError(
        #       'Cannot buy {:.2f}$. Available: {:.2f}UAH'.format(self.daily_amount, self.amount))
        self._min_debt = min(debt, self._min_debt)

        self.amount -= t.price
        self.transactions.append(t)
        print('Amount in the end of the day: {:.2f}'.format(self.amount))

    def handle_expired(self, date, rate_sale):
        for t in self.transactions:
            if (
                    t.date + timedelta(days=self.shift) < date and
                    rate_sale > t.rate_buy and
                    not t.sold
            ):
                print('Selling expired {}'.format(t))
                self.amount += t.sale(rate_sale)

    def close(self, rate_sale_closing):
        """Sell all hanging transaction for the rate specified"""
        print('Closing trading for {} transactions'.format(len(self.hanging)))
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


def parse_args():
    parser = argparse.ArgumentParser(description='TradeAlgo#02v0')
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='which year you want to analyze',
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


def main(year, starting_amount_uah):
    currency = 'usd'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT)
    # ed = datetime.strptime('31.12.{}'.format(year), DATE_FMT)

    last_date_value = df.iloc[[-1]]['date'].item()
    pd_date = pd.to_datetime(last_date_value)
    ed = pd_date.to_pydatetime()
    print(sd.month, ed.month)
    print('Trading at period: [{} - {}]'.format(sd, ed))

    shift = 6  # delay in days between buying and selling
    trader = ShiftTrader(
        starting_amount=starting_amount_uah,
        shift=shift,
    )

    i = 0
    transactions = 0
    skipped = 0
    current_date = sd  # starting date
    k1_return = None
    k1_return_soft = None
    k5_return = None
    k5_return_soft = None
    p10_return = None
    p10_return_soft = None
    exit_period = None
    while current_date <= ed:  # until end date
        rate_sale = df.loc[df['date'] == current_date]['sale'].item()
        rate_buy = df.loc[df['date'] == current_date]['buy'].item()
        print('\n==>{}: {:.2f}/{:.2f}'.format(current_date.strftime(DATE_FMT), rate_buy, rate_sale))
        daily_data = {
            'date': current_date,
            'buy': rate_sale,  # we buy currency, bank sale currency
            'sale': rate_buy,  # we sale currency, bank buy currency
        }
        potential = trader.get_potential(rate_buy)
        print('Potential = {:.2f}'.format(potential))
        trader.trade(daily_data)
        days_passed = current_date - sd  # how many days passed since start
        if exit_period is None and potential > starting_amount_uah:
            exit_period = days_passed
        if k1_return is None and trader.amount >= starting_amount_uah + 1000:
            k1_return = days_passed
        if k1_return_soft is None and potential >= starting_amount_uah + 1000:
            k1_return_soft = days_passed
        if k5_return is None and trader.amount >= starting_amount_uah + 5000:
            k5_return = days_passed
        if k5_return_soft is None and potential >= starting_amount_uah + 5000:
            k5_return_soft = days_passed
        if p10_return is None and trader.amount >= 1.1 * starting_amount_uah:
            p10_return = days_passed
        if p10_return_soft is None and potential >= 1.1 * starting_amount_uah:
            p10_return_soft = days_passed

        i += 1
        current_date += timedelta(days=1)

    print('\nReport for {}:\n'.format(year))
    if trader._min_debt < 0:
        print('Insufficient investments, consider adding {:.2f}'.format(trader._min_debt))
        raise RuntimeError('Relaunch with higher initial amount')
    if k1_return is not None:
        print('1K profit period: {} days'.format(k1_return.days))
    else:
        print('1K HARD is unreachable within given period')
    if k1_return_soft is not None:
        print('1K gain soft period: {} days'.format(k1_return_soft.days))
    else:
        print('1K SOFT is unreachable within given period')

    if k5_return is not None:
        print('5K profit period: {} days'.format(k5_return.days))
    else:
        print('5K HARD is unreachable within given period')
    if k5_return_soft is not None:
        print('5K gain soft period: {} days'.format(k5_return_soft.days))
    else:
        print('5K SOFT is unreachable within given period')

    if p10_return is not None:
        print('10% profit period: {} days'.format(p10_return.days))
    else:
        print('10% HARD is unreachable within given period')
    if p10_return_soft is not None:
        print('10% gain soft period: {} days'.format(p10_return_soft.days))
    else:
        print('10% SOFT is unreachable within given period')

    if exit_period is not None:
        print('Exit period: {} days\n'.format(exit_period.days))
    else:
        print('Cannot exit within given period\n')

    print('Total transactions: {}'.format(len(trader.transactions)))
    print('Hanging transactions: {}'.format(len(trader.hanging)))
    # close period at the last day no matter which rate
    # in order to calculate raw profit
    trader.close(rate_buy)
    print('Initial invested amount: {}'.format(starting_amount_uah))
    print('Amount we have in the end: {:.2f}'.format(trader.amount))
    print('Raw profit: {:.2f}'.format(trader.amount - starting_amount_uah))
    print('Profit, %: {:.2f}'.format(
        trader.amount / starting_amount_uah * 100))


if __name__ == '__main__':
    args = parse_args()
    main(year=args.year, starting_amount_uah=args.amount)
