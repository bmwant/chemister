from datetime import datetime

import attr
import sqlalchemy as sa

from . import metadata
from .resource import resource


@attr.s
class Bid(object):
    amount: float = attr.ib()
    currency: str = attr.ib()
    rate: float = attr.ib()
    phone: str = attr.ib()
    id: int = attr.ib()
    date: str = attr.ib()
    resource: str = attr.ib()


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
