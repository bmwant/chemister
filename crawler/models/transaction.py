from enum import Enum
from typing import Iterable
from operator import attrgetter
from datetime import datetime, timedelta

import sqlalchemy as sa

from utils import get_midnight, get_logger
from crawler.helpers import load_config
from crawler.db import Engine
from . import metadata
from .resource import resource, Resource, get_resource_by_name
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


async def get_bid_by_id(conn, bid_id):
    query = bid.select().where(bid.c.id == bid_id)

    result = await conn.execute(query)
    return await result.fetchone()


async def get_transactions(conn):
    query = transaction.select()
    result = await conn.execute(query)
    return await result.fetchall()


async def get_bid_by_signature(conn, bid_item):
    whereclause = sa.and_(
        bid.c.rate == bid_item['rate'],
        bid.c.amount == bid_item['amount'],
        bid.c.currency == bid_item['currency'],
        bid.c.phone == bid_item['phone'],
        bid.c.bid_type == bid_item['bid_type'],
        bid.c.in_use == True,
    )

    query = bid.select(whereclause)
    result = await conn.execute(query)
    return await result.fetchone()


async def get_bids_for_period(
    conn,
    *,
    start_date,
    end_date,
):
    query = bid.select().where(sa.and_(
        bid.c.created >= start_date,
        bid.c.created <= end_date,
    ))

    result = await conn.execute(query)
    return await result.fetchall()


async def insert_new_transaction(
    conn,
    transaction,
):
    # config = await load_config(conn)

    query = transaction.insert().values(
        amount=transaction.amount,
        currency='USD',
        rate_buy=transaction.rate_buy,
        rate_sale=transaction.rate_sale,
        user_id=1,
    )
    await conn.execute(query)


async def close_transaction(
    conn,
    *,
    transaction_id,
):
    pass
