from datetime import datetime, timedelta

import sqlalchemy as sa

from utils import get_midnight
from crawler.helpers import load_config
from crawler.models.bid import (
    bid,
    get_daily_bids,
    BidType,
    BidStatus,
    GONE_STATUSES,
)


async def get_profit_last_month(conn):
    starting_point = datetime.now() - timedelta(days=30)
    starting_day = get_midnight(starting_point)
    bids = await get_closed_bids_for_period(conn, starting_day=starting_day)
    for bid in bids:
        print(bid)


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
