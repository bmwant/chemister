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


logger = get_logger(__name__)


class BidStatus(Enum):
    NEW = 'new'
    NOTIFIED = 'notified'
    CALLED = 'called'
    REJECTED = 'rejected'
    INACTIVE = 'inactive'
    CLOSED = 'closed'


def get_statuses(*args):
    return [*map(attrgetter('value'), args)]


ACTIVE_STATUSES = (BidStatus.NEW, BidStatus.NOTIFIED, BidStatus.CALLED)

INACTIVE_STATUSES = (BidStatus.REJECTED, BidStatus.INACTIVE, BidStatus.CLOSED)

GONE_STATUSES = (BidStatus.REJECTED, BidStatus.INACTIVE)


class BidType(Enum):
    IN = 'in'
    OUT = 'out'


bid = sa.Table(
    'bid', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    # Return as floats
    sa.Column('rate', sa.Numeric(asdecimal=False), nullable=False,),
    sa.Column('amount', sa.Numeric(asdecimal=False), nullable=False),
    sa.Column('currency', sa.String, nullable=False),
    sa.Column('status', sa.String, nullable=False),
    sa.Column('bid_type', sa.String, nullable=False),
    sa.Column('phone', sa.String, nullable=False),
    sa.Column('created', sa.DateTime, nullable=False, default=datetime.now),
    sa.Column('dry_run', sa.Boolean, nullable=False),
    sa.Column('in_use', sa.Boolean, nullable=False, default=True),
    sa.Column('resource_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='bid_id_pkey'),
    sa.ForeignKeyConstraint(['resource_id'], [resource.c.id],
                            name='bid_resource_id_fkey',
                            ondelete='NO ACTION'),
)


async def get_bid_by_id(conn, bid_id):
    query = bid.select().where(bid.c.id == bid_id)

    result = await conn.execute(query)
    return await result.fetchone()


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


async def insert_new_bid(
    conn,
    new_bid: dict,
    resource: Resource,
):
    config = await load_config(conn)

    resource_item = await get_resource_by_name(conn, resource.name)
    if resource_item is None:
        raise ValueError('Cannot load such a [%s]' % resource)

    query = bid.insert().values(
        rate=new_bid['rate'],
        amount=new_bid['amount'],
        currency=new_bid['currency'],
        phone=new_bid['phone'],
        bid_type=new_bid['bid_type'],
        dry_run=config.DRY_RUN,
        resource_id=resource_item.id,
    )
    await conn.execute(query)


async def get_daily_bids(
    conn,
    *,
    bid_type: BidType=None,
    statuses: Iterable[BidStatus]=None
):
    datetime_today = datetime.now()
    datetime_tomorrow = datetime_today + timedelta(days=1)
    midnight_today = get_midnight(datetime_today)
    midnight_tomorrow = get_midnight(datetime_tomorrow)
    query = bid.select().where(sa.and_(
        bid.c.created > midnight_today,
        bid.c.created <= midnight_tomorrow,
    ))

    if bid_type is not None:
        query = query.where(bid.c.bid_type == bid_type.value)

    if statuses is not None:
        status_values = get_statuses(*statuses)
        query = query.where(bid.c.status.in_(status_values))

    result = await conn.execute(query)
    return await result.fetchall()


async def mark_bids_as(conn, bid_ids: list, bid_status: BidStatus):
    query = bid.update()\
        .where(bid.c.id.in_(bid_ids))\
        .values(status=bid_status.value)

    return (await conn.execute(query)).rowcount


async def mark_bids_as_unused(conn, bid_ids: list):
    query = bid.update()\
        .where(bid.c.id.in_(bid_ids))\
        .values(in_use=False)

    return (await conn.execute(query)).rowcount


async def set_bid_status(conn, bid_id: int, bid_status: BidStatus):
    query = bid.update()\
        .where(bid.c.id == bid_id)\
        .values(status=bid_status.value)

    return (await conn.execute(query)).rowcount


async def mark_daily_bids_as_unused():
    """
    Daily task that will mark all daily bids as unused not to collide with
    newcoming bids.
    """
    bid_ids = []
    async with Engine() as engine:
        async with engine.acquire() as conn:
            return await mark_bids_as_unused(conn, bid_ids)


async def _autoclose_bids():
    """
    Helper function for developer mode simulating closing bids after
    notifications being sent.
    """
    async with Engine() as engine:
        async with engine.acquire() as conn:
            statuses = [BidStatus.NOTIFIED]
            daily_bids = await get_daily_bids(conn, statuses=statuses)

            bid_ids = [b.id for b in daily_bids]
            if bid_ids:
                logger.debug('Closing bids %s', bid_ids)
                await mark_bids_as(conn, bid_ids, BidStatus.CLOSED)
