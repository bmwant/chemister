import pytest

from crawler.helpers import load_config


@pytest.mark.run_loop
async def test_load_config():
    config = await load_config()

    assert hasattr(config, 'DRY_RUN')
    assert hasattr(config, 'MAX_BID_AMOUNT')
    assert isinstance(config.MAX_BID_AMOUNT, float)
