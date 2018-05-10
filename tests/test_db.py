from unittest import mock

import pytest

from crawler.forms.config import config_trafaret
from crawler.models.configs import insert_new_config
from crawler.models.bid import (
    insert_new_bid,
    get_daily_bids,
    get_bid_by_signature,
    get_bid_by_id,
    set_bid_status,
    mark_bids_as,
    BidType,
    BidStatus,
    ACTIVE_STATUSES,
)
from crawler.models.resource import insert_new_resource
from crawler.db import get_engine, close_engine, Engine


@pytest.mark.run_loop
async def test_insert_new_config(pg_engine, user):
    config = {
        'DRY_RUN': True,
        'CLOSED_BIDS_FACTOR': 1,
        'MIN_BID_AMOUNT': 10.0,
        'MAX_BID_AMOUNT': 100.0,
        'TIME_DAY_STARTS': '06:00',
        'TIME_DAY_ENDS': '20:00',
        'REFRESH_PERIOD_MINUTES': 5,
    }
    new_config = config_trafaret.check(config)
    async with pg_engine.acquire() as conn:
        await insert_new_config(conn, new_config=new_config, user_id=user.id)


@pytest.mark.run_loop
async def test_insert_new_resource(pg_engine):
    resource = {
        'name': 'i ua',
        'link': 'http://www.i.ua/',
    }
    async with pg_engine.acquire() as conn:
        result = await insert_new_resource(conn, resource)

    assert len(result) == 1
    assert isinstance(result[0], int)


async def _get_resource_by_name(*args):
    return mock.Mock(id=1)


@pytest.mark.run_loop
async def test_insert_new_bids(pg_engine, resource):
    in_bid = {
        'rate': 26,
        'amount': 100,
        'currency': 'USD',
        'phone': '+380987776655',
        'bid_type': BidType.IN.value,
    }
    out_bid = {
        'rate': 26.1,
        'amount': 100,
        'currency': 'USD',
        'phone': '+380987774433',
        'bid_type': BidType.OUT.value,
    }

    with mock.patch('crawler.models.bid.get_resource_by_name',
                    _get_resource_by_name):
        async with pg_engine.acquire() as conn:
            await insert_new_bid(conn, in_bid, resource=resource)
            await insert_new_bid(conn, out_bid, resource=resource)


@pytest.mark.run_loop
async def test_get_bid_by_signature(pg_engine):
    nonexisting_bid = {
        'rate': 500,
        'amount': 100,
        'currency': 'USD',
        'phone': '+380971112233',
        'bid_type': BidType.OUT.value,
    }
    the_bid = {
        'rate': 26.1,
        'amount': 100,
        'currency': 'USD',
        'phone': '+380987774433',
        'bid_type': BidType.OUT.value,
    }

    async with pg_engine.acquire() as conn:
        result = await get_bid_by_signature(conn, nonexisting_bid)
        assert result is None

        result = await get_bid_by_signature(conn, the_bid)
        assert result is not None


@pytest.mark.run_loop
async def test_set_bid_status(pg_engine):
    bid_id = 1
    async with pg_engine.acquire() as conn:
        await set_bid_status(conn, bid_id=bid_id, bid_status=BidStatus.CLOSED)
        updated_bid = await get_bid_by_id(conn, bid_id=bid_id)
        assert updated_bid.status == BidStatus.CLOSED.value


@pytest.mark.run_loop
async def test_get_bid_by_id(pg_engine):
    async with pg_engine.acquire() as conn:
        bid = await get_bid_by_id(conn, bid_id=1)

        assert bid is not None


@pytest.mark.run_loop
async def test_mark_bids_as_inactive(pg_engine):
    bid_ids = [2, 3, 4, 5]
    async with pg_engine.acquire() as conn:
        rowcount = await mark_bids_as(conn, bid_ids, BidStatus.INACTIVE)
        assert rowcount == len(bid_ids)


@pytest.mark.run_loop
async def test_get_only_daily_active_bids(pg_engine):
    async with pg_engine.acquire() as conn:
        bids = await get_daily_bids(
            conn,
            bid_type=BidType.IN,
            statuses=ACTIVE_STATUSES,
        )


@pytest.mark.run_loop
async def test_engine_closed():
    engine = await get_engine()

    await close_engine(engine)
    assert engine.closed


@pytest.mark.run_loop
async def test_engine_used_with_context_manager():
    async with Engine() as engine:
        assert engine.name == 'postgresql'

    assert engine.closed
