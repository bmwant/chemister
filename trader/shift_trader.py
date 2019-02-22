from datetime import datetime, timedelta

from crawler.models.transaction import NewTransaction
from trader import BaseTrader
from utils import get_midnight


class ShiftTrader_v0(BaseTrader):
    def __init__(self, starting_amount, shift):
        self.amount = starting_amount  # operation money we use to buy currency
        self.shift = shift  # days we wait between buying/selling
        self._min_debt = 0
        super().__init__()

    async def daily(self):
        print('Doing daily routine here')
        # fetch rate from cache
        daily_data = {
            'date': get_midnight(datetime.now()),
            'sale': 26.8,
            'buy': 26.7,
        }
        await self.trade(daily_data=daily_data)

    async def trade(self, daily_data):
        date = daily_data['date']
        # our perspective
        rate_sale = daily_data['buy']
        rate_buy = daily_data['sale']
        transactions = await self.transactions()
        import pdb; pdb.set_trace()
        for t in transactions:
            print(t)
        for t in transactions:
            if (
                t.date + timedelta(days=self.shift) == date and
                rate_sale > t.rate_buy
            ):
                self.amount += t.sale(rate_sale)

        # handle expired transactions
        await self.handle_expired(date, rate_sale)

        # buy some amount of currency
        t = NewTransaction(
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
        await self.add_transaction(t)
        print('Amount in the end of the day: {:.2f}'.format(self.amount))

    async def handle_expired(self, date, rate_sale):
        transactions = await self.transactions()
        for t in transactions:
            if (
                t.date + timedelta(days=self.shift) < date and
                rate_sale > t.rate_buy and
                not t.sold
            ):
                print('Selling expired {}'.format(t))
                self.amount += t.sale(rate_sale)

    async def close(self, rate_sale_closing):
        """Sell all hanging transaction for the rate specified"""
        hanging = await self.hanging()
        print('Closing trading for {} transactions'.format(len(hanging)))
        for t in hanging:
            self.amount += t.sale(rate_sale_closing)

    @property
    def daily_amount(self):
        return 100

    async def get_potential(self, rate_sale):
        hanging = await self.hanging()
        return self.amount + sum([t.sale(rate_sale, dry_run=True)
                                  for t in hanging])
