from datetime import datetime

import pytest

from utils import get_midnight
from crawler.models.transaction import (
    transaction,
    insert_new_transaction,
    get_hanging_transactions,
    NewTransaction,
)


@pytest.mark.run_loop
async def test_querying_hanging_transactions(pg_engine):

    async with pg_engine.acquire() as conn:
        transactions = await get_hanging_transactions(conn)
        assert transactions


@pytest.mark.run_loop
async def test_inserting_new_transaction(pg_engine):
    async with pg_engine.acquire() as conn:
        date = get_midnight(datetime.now())
        new_transaction = NewTransaction(
            amount=100,
            rate_buy=27.8,
            rate_sale=27.7,
            date=date,
        )
        r = await insert_new_transaction(conn, new_transaction)
        assert r


@pytest.mark.run_loop
async def test_updating_existing_transaction(pg_engine):
    date = get_midnight(datetime.now())
    async with pg_engine.acquire() as conn:
        new_transaction = NewTransaction(
            amount=100,
            rate_buy=27.8,
            rate_sale=27.7,
            date=date,
        )
        r = await insert_new_transaction(conn, new_transaction)
        t_id = r[0]
        query = transaction.update() \
            .where(transaction.c.id == t_id) \
            .values(amount=150)
        r = await conn.execute(query)
        assert r.rowcount == 1
