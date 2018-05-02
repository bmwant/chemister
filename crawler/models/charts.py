from datetime import datetime, timedelta
from collections import defaultdict

import sqlalchemy as sa

import settings
from utils import get_midnight
from crawler.models.bid import (
    bid,
    BidType,
    BidStatus,
)


async def get_profit_last_month(conn):
    days = 30
    now = datetime.now()
    starting_point = now - timedelta(days=days)
    starting_day = get_midnight(starting_point)
    bids = await get_closed_bids_for_period(conn, starting_day=starting_day)
    data = defaultdict(int)

    for bid in bids:
        day_key = bid.created.strftime(settings.DEFAULT_DATE_FORMAT)
        if bid.bid_type == BidType.IN.value:
            data[day_key] -= bid.amount * bid.rate
        elif bid.bid_type == BidType.OUT.value:
            data[day_key] += bid.amount * bid.rate

    return [{'date': key, 'value': value} for key, value in data.items()]


async def get_closed_bids_for_period(
    conn,
    *,
    starting_day
):
    query = bid.select().where(sa.and_(
        bid.c.created > starting_day,
        bid.c.status == BidStatus.CLOSED.value,
    ))

    result = await conn.execute(query)
    return await result.fetchall()
