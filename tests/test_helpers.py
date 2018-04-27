import pytest

from crawler.helpers import load_config


@pytest.mark.run_loop
async def test_load_config(pg_engine):
    async with pg_engine.acquire() as conn:
        config = await load_config(conn)

    assert hasattr(config, 'DRY_RUN')
    assert hasattr(config, 'MIN_BID_AMOUNT')
    assert hasattr(config, 'MAX_BID_AMOUNT')
    assert isinstance(config.MAX_BID_AMOUNT, float)
