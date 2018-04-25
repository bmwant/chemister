import pytest

from crawler.models.fund import get_current_fund_amount


@pytest.mark.run_loop
async def test_get_current_fund(pg_engine):

    async with pg_engine.acquire() as conn:
        fund = await get_current_fund_amount(conn)
        assert isinstance(fund, float)
