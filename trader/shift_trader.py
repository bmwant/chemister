from datetime import datetime, timedelta

from crawler.notifier import notify, format_message
from crawler.models.transaction import NewTransaction
from trader import BaseTrader
from utils import get_midnight, get_date_cache_key


class ShiftTrader_v0(BaseTrader):
    def __init__(self, starting_amount, shift):
        super().__init__()
        self.shift = shift  # days we wait between buying/selling
        # todo: this should be fund table
        self.amount = starting_amount  # operation money we use to buy currency
        # todo: init notifier

    async def daily(self):
        # fetch rate from cache
        now = datetime.now()
        key = get_date_cache_key(now)
        data = await self.cache.get(key)

        # bank's perspective
        sale = None
        buy = None

        for item in data:
            if item['ccy'] == 'USD':
                sale = float(item['sale'])
                buy = float(item['buy'])
                break
        daily_data = {
            'date': get_midnight(now),
            'sale': sale,
            'buy': buy,
        }
        await self.trade(daily_data=daily_data)

    async def notify(self, message):
        await notify(message)

    async def trade(self, daily_data):
        date = daily_data['date']
        # our perspective
        rate_sale = daily_data['buy']
        rate_buy = daily_data['sale']

        self.logger.info('Trading on %.2f/%.2f', rate_sale, rate_buy)
        await notify(f'{DOLLAR_ICON} {rate_sale}/{rate_buy}')

        transactions = await self.transactions()
        for t in transactions:
            open_date = get_midnight(t.date_opened)
            if (
                open_date + timedelta(days=self.shift) == date and
                rate_sale > t.rate_buy
            ):
                amount = await self.sale_transaction(t, rate_sale)
                await notify(format_message('sale',amount,rate_sale,'pb'))

        # handle expired transactions
        await self.handle_expired(date, rate_sale)

        # buy some amount of currency
        t = NewTransaction(
            rate_buy=rate_buy,
            rate_sale=rate_sale,
            amount=self.daily_amount,
            date=date,
        )
        # if debt < 0:
        #    raise ValueError(
        #       'Cannot buy {:.2f}$. Available: {:.2f}UAH'.format(self.daily_amount, self.amount))

        self.amount -= t.price
        await notify(format_message('buy',self.daily_amount,rate_buy,'pb'))
        await self.add_transaction(t)
        self.logger.info('Amount in the end of the day: %.2f', self.amount)
        potential = await self.get_potential(rate_sale)
        self.logger.info('Potential is %.2f', potential)
        # todo: self.notifier.notify_telegram(message)
        await self.notify(f'Current potential is {potential}')

    async def handle_expired(self, date, rate_sale):
        transactions = await self.hanging()
        if transactions:
            self.logger.info('Handling expired transactions:')
        else:
            self.logger.info('No expired transactions.')

        for t in transactions:
            if (
                t.date_opened + timedelta(days=self.shift) < date and
                rate_sale > t.rate_buy
            ):
                await self.sale_transaction(t, rate_close=rate_sale)

    async def close(self, rate_sale_closing):
        """Sell all hanging transaction for the rate specified"""
        hanging = await self.hanging()
        print('Closing trading for {} transactions'.format(len(hanging)))
        # todo: close all

    @property
    def daily_amount(self):
        return 100

    async def get_potential(self, rate_sale):
        hanging = await self.hanging()
        return self.amount + sum([
            await self.sale_transaction(t, rate_close=rate_sale, dry_run=True)
            for t in hanging
        ])
