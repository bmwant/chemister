from abc import ABC, abstractmethod

from crawler.db import get_engine
from crawler.cache import Cache
from crawler.models.transaction import (
    NewTransaction,
    get_transactions,
    insert_new_transaction,
    close_transaction,
    get_hanging_transactions,
)
from utils import LoggableMixin


class BaseTrader(ABC, LoggableMixin):
    def __init__(self):
        self.amount = 0
        self.engine = None
        self.cache = None
        super().__init__()

    async def init(self):
        self.engine = await get_engine()
        self.cache = Cache()  # todo: what about without a pool
        # todo: maybe singletone for all traders
        await self.cache._create_pool()

    @abstractmethod
    def trade(self, daily_data):
        pass

    @abstractmethod
    def daily(self):
        """
        Daily periodic task which will be invoked automatically. Interface for the `Factory` when
        creating trading instances to be triggered periodically.
        """

    @abstractmethod
    def notify(self, *args):
        """
        Send updates via preferred channel about trade results.
        """

    async def sale_transaction(self, t, rate_close, dry_run=False):
        amount = t.amount * rate_close  # resulting amount of transaction
        price = t.amount * t.rate_sale  # initial price of transaction
        profit = amount - price
        if not dry_run:
            async with self.engine.acquire() as conn:
                self.logger.info(
                    'Selling {amount:.2f} ({rate_sale:.2f}) '
                    'at {rate_close:.2f}; '
                    'total: {total:.2f}; '
                    'profit: {profit:.2f}'.format(
                        amount=t.amount,
                        rate_sale=t.rate_sale,
                        rate_close=rate_close,
                        total=amount,
                        profit=profit,
                ))
                await close_transaction(
                    conn,
                    t_id=t.id,
                    rate_close=rate_close,
                )
                self.amount += amount
        return amount

    async def add_transaction(self, t: NewTransaction):
        async with self.engine.acquire() as conn:
            await insert_new_transaction(conn, t)

    async def hanging(self):
        async with self.engine.acquire() as conn:
            return await get_hanging_transactions(conn)

    async def transactions(self):
        """
        History of all transactions
        """
        async with self.engine.acquire() as conn:
            return await get_transactions(conn)
