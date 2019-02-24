from datetime import datetime

import sqlalchemy as sa

from utils import get_logger, get_midnight
from . import metadata


logger = get_logger(__name__)


default_date = lambda: get_midnight(datetime.now())


rate = sa.Table(
    'phone', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('date', sa.DateTime, nullable=False, default=default_date),
    sa.Column('bank', sa.String, nullable=False),
    sa.Column('currency', sa.String, nullable=False),
    sa.Column('rate_buy', sa.Numeric(asdecimal=False), nullable=False,),
    sa.Column('rate_sale', sa.Numeric(asdecimal=False), nullable=False),

    sa.PrimaryKeyConstraint('id', name='rate_id_pkey'),
)


async def insert_new_rate(
    conn, *,
    bank,
    rate_buy,
    rate_sale,
):
    query = rate.insert().values(
        bank=bank,
        currency='USD',
        rate_buy=rate_buy,
        rate_sale=rate_sale,
    )
    result = await conn.execute(query)
    row_id = (await result.fetchone())[0]
    return row_id


async def get_rates(conn):
    query = rate.select()
    result = await conn.execute(query)
    return await result.fetchall()
