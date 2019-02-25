from enum import Enum
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
    sa.Column('currency', sa.String, nullable=False),
    sa.Column('bank', sa.String, nullable=False, default='default'),
    sa.Column('amount',
              sa.Numeric(asdecimal=False), nullable=False, default=0),
    sa.Column('created', sa.DateTime, nullable=False, default=datetime.now),

    sa.Column('user_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='fund_id_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [user.c.id],
                            name='fund_user_id_fkey',
                            ondelete='NO ACTION'),
)


class Currency(Enum):
    UAH = 'UAH'
    USD = 'USD'


async def get_bank_fund(
    conn,
    *,
    bank: str,
    currency: Currency,
):
    whereclause = sa.and_(
        fund.c.bank == bank,
        func.c.currency == currency.value,
    )
    query = fund.select().where(whereclause)
    result = await conn.execute(query)
    return await result.fetchall()


async def get_fund(
    conn, 
    *,
    currency: Currency
):
    query = fund.select().where(fund.c.currency == currency.value)
    result = await conn.execute(query)
    return await result.fetchall()
