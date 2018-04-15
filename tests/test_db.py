import pytest
from crawler.models.configs import insert_new_config
from crawler.models.bid import insert_new_bid
from crawler.models.resource import insert_new_resource


@pytest.mark.run_loop
async def test_insert_new_config():
    config = {
        'DRY_RUN': True,
        'CLOSED_BIDS_FACTOR': 1,
        'MIN_BID_AMOUNT': 10,
        'MAX_BID_AMOUNT': 100,
        'TIME_DAY_ENDS': '20:00',
        'REFRESH_PERIOD_MINUTES': 5,
    }
    await insert_new_config(config)


@pytest.mark.run_loop
async def test_insert_new_resource():
    resource = {
        'name': 'i ua',
        'url': 'http://www.i.ua/',
    }
    result = await insert_new_resource(resource)
    assert len(result) == 1
    assert isinstance(result[0], int)


@pytest.mark.run_loop
async def test_insert_new_bid():
    bid = {
        'rate': 26,
        'amount': 100,
        'currency': 'USD',
        'phone': '+380987776655'
    }
    await insert_new_bid(bid)
