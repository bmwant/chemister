import pytest

from crawler.models.stats import (
    get_daily_profit,
    get_current_profit,
)


@pytest.mark.run_loop
async def test_get_daily_profit(pg_engine):
    async with pg_engine.acquire() as conn:
        profit = await get_daily_profit(conn)

    assert isinstance(profit, float)
    print(profit)


@pytest.mark.run_loop
async def test_get_current_profit(pg_engine):
    async with pg_engine.acquire() as conn:
        profit = await get_current_profit(conn)

    assert isinstance(profit, float)
    print(profit)
