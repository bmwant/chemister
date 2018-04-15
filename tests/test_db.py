import pytest
from crawler.models.bid import insert_new_bid
from crawler.models.resource import insert_new_resource


@pytest.mark.run_loop
async def test_insert_new_bid():
    bid = {
        'rate': 26,
        'amount': 100,
        'currency': 'USD',
        'phone': '+380987776655'
    }
    await insert_new_bid(bid)


@pytest.mark.run_loop
async def test_insert_new_resource():
    resource = {
        'name': 'i ua',
        'url': 'http://www.i.ua/',
    }
    result = await insert_new_resource(resource)
    assert len(result) == 1
    assert isinstance(result[0], int)
