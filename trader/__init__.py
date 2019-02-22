from abc import ABC, abstractmethod

from crawler.db import get_engine
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
        super().__init__()

    async def init(self):
        self.engine = await get_engine()

    @abstractmethod
    def trade(self, daily_data):
        pass

    @abstractmethod
    def daily(self):
        """
        Daily periodic task which will be invoked automatically. Interface for the `Factory` when
        creating trading instances to be triggered periodically.
        """

    async def sale_transaction(self, t, rate_close, dry_run=False):
        amount = t.amount * rate_close
        price = t.amount * t.rate_buy
        profit = amount - price
        if not dry_run:
            async with self.engine.acquire() as conn:
                print(
                    'Selling {amount:.2f}({rate_buy:.2f}) at {rate_close:.2f}; '
                    'total: {total:.2f}; profit: {profit:.2f}'.format(
                        amount=t.amount,
                        rate_buy=t.rate_buy,
                        rate_close=rate_close,
                        total=amount,
                        profit=profit,
                ))
                await close_transaction(
                    conn,
                    transaction_id=t.id,
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
