from enum import Enum
from datetime import datetime, timedelta

import sqlalchemy as sa

from utils import get_midnight, get_logger
from crawler.helpers import load_config
from . import metadata
from .resource import resource


logger = get_logger(__name__)


class BidStatus(Enum):
    NEW = 'new'
    NOTIFIED = 'notified'
    CALLED = 'called'
    REJECTED = 'rejected'
    INACTIVE = 'inactive'
    CLOSED = 'closed'


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
    )

    query = bid.select(whereclause)
    result = await conn.execute(query)
    return await result.fetchone()


async def insert_new_bid(
    conn,
    new_bid: dict,
    bid_type: BidType=None,
    resource=None,
):
    config = await load_config(conn)

    if bid_type is None:
        bid_type_value = new_bid['bid_type']
    else:
        bid_type_value = bid_type.value

    query = bid.insert().values(
        rate=new_bid['rate'],
        amount=new_bid['amount'],
        currency=new_bid['currency'],
        phone=new_bid['phone'],
        bid_type=bid_type_value,
        dry_run=config.DRY_RUN,
        resource_id=1,
    )
    await conn.execute(query)


async def get_daily_bids(conn, bid_type: BidType):
    datetime_today = datetime.now()
    datetime_tomorrow = datetime_today + timedelta(days=1)
    midnight_today = get_midnight(datetime_today)
    midnight_tomorrow = get_midnight(datetime_tomorrow)
    query = bid.select().where(sa.and_(
        bid.c.created > midnight_today,
        bid.c.created <= midnight_tomorrow,
        bid.c.bid_type == bid_type.value
    ))
    result = await conn.execute(query)
    return await result.fetchall()


async def mark_bids_as_inactive(conn, bid_ids: list):
    query = bid.update()\
        .where(bid.c.id.in_(bid_ids))\
        .values(status=BidStatus.INACTIVE.value)

    return (await conn.execute(query)).rowcount


async def set_bid_status(conn, bid_id: int, bid_status: BidStatus):
    query = bid.update()\
        .where(bid.c.id == bid_id)\
        .values(status=bid_status.value)

    return (await conn.execute(query)).rowcount
