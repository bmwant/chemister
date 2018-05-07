import pytest

from crawler.models.charts import (
    get_profit_last_month,
    get_notifications_last_month,
)


@pytest.mark.run_loop
async def test_get_profit_last_month(pg_engine):

    async with pg_engine.acquire() as conn:
        res = await get_profit_last_month(conn)


@pytest.mark.run_loop
async def test_get_notify_events(pg_engine):
    async with pg_engine.acquire() as conn:
        res = await get_notifications_last_month(conn)
