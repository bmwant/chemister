import pytest

from crawler.models.charts import get_profit_last_month


@pytest.mark.run_loop
async def test_get_profit_last_month(pg_engine):

    async with pg_engine.acquire() as conn:
        res = await get_profit_last_month(conn)
