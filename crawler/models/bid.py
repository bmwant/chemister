from datetime import datetime

import sqlalchemy as sa

from . import metadata
from .resource import resource
from crawler.db import get_engine
from crawler.helpers import load_config


bid = sa.Table(
    'bid', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('rate', sa.Float, nullable=False),
    sa.Column('amount', sa.Float, nullable=False),
    sa.Column('currency', sa.String, nullable=False),
    sa.Column('phone', sa.String, nullable=False),
    sa.Column('created', sa.DateTime, nullable=False, default=datetime.now),
    sa.Column('dry_run', sa.Boolean, nullable=False),
    sa.Column('resource_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='bid_id_pkey'),
    sa.ForeignKeyConstraint(['resource_id'], [resource.c.id],
                            name='bid_resource_id_fkey',
                            ondelete='NO ACTION'),
)


async def insert_new_bid(new_bid, resource=None):
    engine = await get_engine()
    config = await load_config()

    async with engine.acquire() as conn:
        query = bid.insert().values(
            rate=new_bid['rate'],
            amount=new_bid['amount'],
            currency=new_bid['currency'],
            phone=new_bid['phone'],
            dry_run=config.DRY_RUN,
            resource_id=1,
        )
        await conn.execute(query)
