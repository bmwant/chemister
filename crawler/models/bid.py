from enum import Enum
from datetime import datetime, timedelta

import sqlalchemy as sa

from utils import get_midnight
from . import metadata
from .resource import resource
from crawler.db import get_engine
from crawler.helpers import load_config


class BidStatus(Enum):
    pass


class BidType(Enum):
    IN = 'in'
    OUT = 'out'


bid = sa.Table(
    'bid', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('rate', sa.Float, nullable=False),
    sa.Column('amount', sa.Float, nullable=False),
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


async def insert_new_bid(new_bid, bid_type, resource=None):
    engine = await get_engine()
    config = await load_config()

    async with engine.acquire() as conn:
        query = bid.insert().values(
            rate=new_bid['rate'],
            amount=new_bid['amount'],
            currency=new_bid['currency'],
            phone=new_bid['phone'],
            bid_type=bid_type,
            dry_run=config.DRY_RUN,
            resource_id=1,
        )
        await conn.execute(query)


async def get_daily_bids(bid_type):
    engine = await get_engine()

    datetime_today = datetime.now()
    datetime_yesterday = datetime_today - timedelta(days=1)
    midnight_today = get_midnight(datetime_today)
    midnight_yesterday = get_midnight(datetime_yesterday)
    async with engine.acquire() as conn:
        query = bid.select().where(sa.and_(
            bid.c.created > midnight_yesterday,
            bid.c.created <= midnight_today
        ))
        result = await conn.execute(query)
        return await result.fetchall()
