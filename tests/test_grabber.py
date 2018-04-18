import pytest

from crawler.grabber.dummy import DummyGrabber


@pytest.mark.run_loop
async def test_insert_new_bids_with_asyncio_gather(pg_engine):
    grabber = DummyGrabber(None, engine=pg_engine)

    bids = [
        {
            'rate': 26,
            'amount': 300,
            'currency': 'USD',
            'phone': '+380987776655',
            'bid_type': 'in',
        },
        {
            'rate': 26.1,
            'amount': 300,
            'currency': 'USD',
            'phone': '+380987774433',
            'bid_type': 'out',
        }
    ]

    await grabber.insert_new_bids(bids)
