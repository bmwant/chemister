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
from crawler.models.event import (
    event,
    EventType,
)


DAYS_IN_MONTH = 30


def _get_starting_day(days_passed=DAYS_IN_MONTH):
    now = datetime.now()
    starting_point = now - timedelta(days=DAYS_IN_MONTH)
    starting_day = get_midnight(starting_point)
    return starting_day


async def get_profit_last_month(conn):
    starting_day = _get_starting_day()
    bids = await get_closed_bids_for_period(conn, starting_day=starting_day)
    data = defaultdict(int)

    for bid in bids:
        day_key = bid.created.strftime(settings.DEFAULT_DATE_FORMAT)
        if bid.bid_type == BidType.IN.value:
            data[day_key] -= bid.amount * bid.rate
        elif bid.bid_type == BidType.OUT.value:
            data[day_key] += bid.amount * bid.rate

    # return [{'date': key, 'value': value} for key, value in data.items()] * 30
    return [
        {'date': '01/05/18', 'value': 500},
        {'date': '02/05/18', 'value': 600},
        {'date': '03/05/18', 'value': 700},
        {'date': '04/05/18', 'value': 300},
        {'date': '05/05/18', 'value': -100},
        {'date': '06/05/18', 'value': -500},
        {'date': '07/05/18', 'value': 120},
        {'date': '08/05/18', 'value': 400},
        {'date': '09/05/18', 'value': 1200},
        {'date': '10/05/18', 'value': 500},
        {'date': '11/05/18', 'value': 500},
        {'date': '12/05/18', 'value': 700},
        {'date': '13/05/18', 'value': 710},
        {'date': '14/05/18', 'value': 800},
        {'date': '15/05/18', 'value': 500},
        {'date': '16/05/18', 'value': 505},
        {'date': '17/05/18', 'value': 10},
    ]


async def get_bids_statuses_last_month(conn):
    starting_day = _get_starting_day()
    bids = await get_closed_bids_for_period(conn, starting_day=starting_day)
    data = defaultdict(int)

    for bid in bids:
        data[bid.status] += 1

    # return [data]  # for donut chart
    # return [{'label': key, 'value': value} for key, value in data.items()]
    return [{
        'notified': 50,
        'called': 3,
        'closed': 10,
        'rejected': 5,
        'inactive': 15,
    }]


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


async def get_notifications_last_month(conn):
    starting_day = _get_starting_day()

    query_notified = event.select().where(sa.and_(
        event.c.created > starting_day,
        event.c.event_type == EventType.NOTIFIED.value,
    ))

    query_called = event.select().where(sa.and_(
        event.c.created > starting_day,
        event.c.event_type == EventType.CALLED.value,
    ))

    result_notified = await conn.execute(query_notified)
    result_called = await conn.execute(query_called)

    events_notified = await result_notified.fetchall()
    events_called = await result_called.fetchall()

    print(events_called)
    print(events_notified)
    return []
