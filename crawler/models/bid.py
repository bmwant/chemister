import sqlalchemy as sa
import attr

from . import metadata
from .resource import resource


@attr.s
class Bid(object):
    amount: float = attr.ib()
    currency: str = attr.ib()
    rate: float = attr.ib()
    phone: str = attr.ib()
    id: int = attr.ib(default=1)
    date: str = attr.ib(default='17 Apr 2018')
    resource: str = attr.ib(default='i.ua')


bid = sa.Table(
    'bid', metadata,
    sa.Column('id', sa.Integer),
    sa.Column('rate', sa.Float),
    sa.Column('amount', sa.Float),
    sa.Column('currency', sa.String),
    sa.Column('phone', sa.String),
    sa.Column('created', sa.DateTime),
    sa.Column('dry_run', sa.Boolean),
    sa.Column('resource_id', sa.Integer, nullable=False),

    sa.PrimaryKeyConstraint('id', name='bid_id_pkey'),
    sa.ForeignKeyConstraint(['resource_id'], [resource.c.id],
                            name='bid_resource_id_fkey',
                            ondelete='SET NULL'),
)
