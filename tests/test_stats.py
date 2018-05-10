import statistics

import pytest

from crawler.models.stats import (
    _f,
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


def test_info_calculation_empty_lists():
    assert _f(min, []) == 0
    assert _f(statistics.mean, []) == 0
    assert _f(max, []) == 0


def test_info_calculation():
    data = [2, 4, 4, 6]
    assert _f(min, data) == 2
    assert _f(statistics.mean, data) == 4
    assert _f(max, data) == 6
