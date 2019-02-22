"""
https://aiopg.readthedocs.io/en/stable/sa.html
"""
from enum import Enum
from typing import Iterable
from operator import attrgetter
from datetime import datetime, timedelta

import sqlalchemy as sa

import settings
from utils import get_midnight, get_logger
from crawler.helpers import load_config
from . import metadata
from .user import user


logger = get_logger(__name__)


transaction = sa.Table(
    'transaction', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    # Return as floats
    sa.Column('amount', sa.Numeric(asdecimal=False), nullable=False,),
    sa.Column('rate_buy', sa.Numeric(asdecimal=False), nullable=False,),
    sa.Column('rate_sale', sa.Numeric(asdecimal=False), nullable=False),
    sa.Column('rate_close', sa.Numeric(asdecimal=False), nullable=True),
    sa.Column('currency', sa.String, nullable=False),
    sa.Column('date_opened', sa.DateTime, nullable=False, default=datetime.now),
    sa.Column('date_closed', sa.DateTime, nullable=True),
    sa.Column('user_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='transaction_id_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [user.c.id],
                            name='transaction_user_id_fkey',
                            ondelete='NO ACTION'),
)


class NewTransaction(object):
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
            self.date.strftime(settings.DEFAULT_DATE_FORMAT),
            self.amount,
            self.rate_buy
        )


async def get_transactions(conn):
    query = transaction.select()
    result = await conn.execute(query)
    return await result.fetchall()


async def get_hanging_transactions(conn):
    whereclause = sa.and_(
        transaction.c.date_closed == None,
        transaction.c.rate_close == None,
    )
    query = transaction.select().where(whereclause)

    result = await conn.execute(query)
    return await result.fetchall()


async def insert_new_transaction(
    conn,
    t: NewTransaction,
):
    # config = await load_config(conn)

    query = transaction.insert().values(
        amount=t.amount,
        currency='USD',
        rate_buy=t.rate_buy,
        rate_sale=t.rate_sale,
        user_id=1,
    )
    result = await conn.execute(query)
    return await result.fetchone()


async def close_transaction(
    conn,
    *,
    transaction_id,
    rate_close,
):
    date_closed = datetime.now()
    query = transaction.update() \
        .where(transaction.c.id == transaction_id) \
        .values(rate_close=rate_close, date_closed=date_closed)
    await conn.execute(query)
