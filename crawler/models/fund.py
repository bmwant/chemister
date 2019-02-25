from enum import Enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import desc

from utils import get_logger
from . import metadata
from .user import user
from .transaction import get_transaction_by_id


logger = get_logger(__name__)


class FundType(Enum):
    TRADE = 'trade'
    INVEST = 'invest'


class Currency(Enum):
    UAH = 'UAH'
    USD = 'USD'


fund = sa.Table(
    'fund', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('currency', sa.String, nullable=False),
    sa.Column('bank', sa.String, nullable=False, default='default'),
    sa.Column('amount',
              sa.Numeric(asdecimal=False), nullable=False, default=0),
    sa.Column('created', sa.DateTime, nullable=False, default=datetime.now),
    sa.Column('fund_type', 
              sa.String, nullable=False, default=FundType.TRADE.value),

    sa.Column('user_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='fund_id_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [user.c.id],
                            name='fund_user_id_fkey',
                            ondelete='NO ACTION'),
)


async def insert_new_investment(
    conn,
    *,
    amount: float,
    currency: Currency,
    bank: str,
    user_id: int,
):
    return await insert_new_fund(
        amount=amount,
        currency=currency,
        bank=bank,
        fund_type=FundType.INVEST,
        user_id=user_id,
    )


async def insert_new_fund(
    conn,
    *,
    amount: float,
    currency: Currency,
    bank: str,
    fund_type: FundType,
    user_id: int,
):
    query = fund.insert().values(
        amount=amount,
        currency=currency.value,
        bank=bank,
        fund_type=fund_type.value,
        user_id=user_id,
    )
    result = await conn.execute(query)
    row_id = (await result.fetchone())[0]
    return row_id


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


async def get_investments(conn):
    query = fund.select() \
        .where(fund.c.fund_type == FundType.INVEST.value) \
        .order_by(sa.desc(fund.c.created))
    result = await conn.execute(query)
    return await result.fetchall()


async def process_buy(
    conn,
    *,
    t_id: int,
    base_currency: Currency,
):
    t = await get_transaction_by_id(conn, t_id=t_id)
    amount = t.amount * t.rate_buy
    fund_amount = await get_bank_fund(bank=t.bank, currency=base_currency)
    if fund_amount >= amount:
        # decrease fund in base currency
        await insert_new_fund(
            conn,
            amount=amount,
            currency=base_currency,
            bank=t.bank,
            fund_type=FundType.TRADE,
            user_id=t.user_id,
        )
        # increase fund in target currency
        target_currency = ggg(t.currency)
        await insert_new_fund(
            conn,
            amount=t.amount,
            currency=t.currency,
            bank=t.bank,
            fund_type=FundType.TRADE,
            user_id=t.user_id,
        )
        return True
    return False


async def process_sale(
    conn,
    *,
    t_id: int,
):
    t = get_transaction_by_id(conn, t_id=t_id)
    base_currency = Currency.UAH  # todo: this is not the end
    amount = t.amount * rate_close
    # increase fund in base currency
    await insert_new_fund(
        conn,
        amount=amount,
        currency=base_currency,
        bank=t.bank,
        fund_type=FundType.TRADE,
        user_id=t.user_id,
    )
    # decrease fund in target currency
    currency = ggg(t.currency)
    await insert_new_fund(
        conn,
        amount=-t.amount,
        currency=currency,
        bank=t.bank,
        fund_type=FundType.TRADE,
        user_id=t.user_id,
    )
    return True
