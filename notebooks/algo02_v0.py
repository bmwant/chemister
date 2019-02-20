from datetime import datetime, timedelta

import pandas as pd

from download_rates import DATE_FMT


class Transaction(object):
    def __init__(self, amount, rate_buy, rate_sale, date):
        self.amount = amount  # amount of currency we bought
        self.rate_buy = rate_buy  # rate when trading
        self.rate_sale = rate_sale  # selling rate when trading to calculate future profit
        self.date = date
        self._sold = False

    def sale(self, rate_sale):
        amount = self.amount * rate_sale
        profit = amount - self.price  # what we gain
        print('Selling {amount:.2f} at {rate:.2f}; '
              'total: {total:.2f}; profit: {profit:.2f}'.format(
            amount=self.amount,
            rate=rate_sale,
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

    def trade(self, daily_data):
        date = daily_data['date']
        # our perspective
        rate_sale = daily_data['buy']
        rate_buy = daily_data['sale']
        for t in self.transactions:
            if t.date + timedelta(days=self.shift) == date and rate_sale > t.rate_buy:
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
        if t.price > self.amount:
            raise ValueError('Cannot buy {:.2f}$. Available: {:.2f}UAH'.format(self.daily_amount, self.amount))

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
    
    @property
    def daily_amount(self):
        return 100
    
    @property
    def hanging(self):
        return list(filter(lambda t: not t.sold, self.transactions))


def main():
    year = 2017
    currency = 'usd'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT) 
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT) 
    ed = datetime.strptime('31.12.{}'.format(year), DATE_FMT)

    shift = 6  # delay in days between buying and selling
    starting_amount_uah = 35000  # initial value of money we have
    trader = ShiftTrader(
        starting_amount=starting_amount_uah,
        shift=shift,
    )

    i = 0
    transactions = 0
    skipped = 0
    current_date = sd  # starting date
    while current_date <= ed:  # until end date
        rate_sale = df.loc[df['date'] == current_date.strftime(DATE_FMT)]['sale'].item()
        rate_buy = df.loc[df['date'] == current_date.strftime(DATE_FMT)]['buy'].item()
        print('\n==>{}: {:.2f}/{:.2f}'.format(current_date.strftime(DATE_FMT), rate_buy, rate_sale))
        daily_data = {
            'date': current_date,
            'buy': rate_sale,  # we buy currency, bank sale currency
            'sale': rate_buy,  # we sale currency, bank buy currency
        }
        trader.trade(daily_data)

        i += 1
        current_date += timedelta(days=1)

    # close period to calculate raw profit in uah
    print('Total transactions: {}'.format(len(trader.transactions)))
    print('Hanging transactions: {}'.format(len(trader.hanging)))
    print('Amount we have in the end: {:.2f}'.format(trader.amount))
    print('Raw profit: {:.2f}'.format(trader.amount - starting_amount_uah))
    print('Profit, %: {:.2f}'.format(trader.amount / starting_amount_uah * 100)) 


if __name__ == '__main__':
    main()

