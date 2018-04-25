from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import desc

from utils import get_logger
from . import metadata
from .user import user


logger = get_logger(__name__)


fund = sa.Table(
    'fund', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('amount',
              sa.Numeric(asdecimal=False), nullable=False, default=0),
    sa.Column('created', sa.DateTime, nullable=False, default=datetime.now),

    sa.Column('user_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='fund_id_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [user.c.id],
                            name='fund_user_id_fkey',
                            ondelete='NO ACTION'),
)


async def get_current_fund_amount(conn):
    query = fund.select().order_by(desc(fund.c.created))
    result = await conn.execute(query)
    return (await result.fetchone()).amount
