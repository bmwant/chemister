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
    starting_point = now - timedelta(days=days_passed)
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

    return [{'date': key, 'value': value} for key, value in data.items()]


async def get_bids_statuses_last_month(conn):
    starting_day = _get_starting_day()
    bids = await get_closed_bids_for_period(conn, starting_day=starting_day)
    data = defaultdict(int)

    for bid in bids:
        data[bid.status] += 1

    return [data]  # for donut chart


async def get_closed_bids_for_period(
    conn,
    *,
    starting_day
):
    query = bid.select().where(sa.and_(
        bid.c.created > starting_day,
        bid.c.status == BidStatus.CLOSED.value,
    )).order_by(sa.asc(bid.c.created))

    result = await conn.execute(query)
    return await result.fetchall()


async def get_notifications_last_month(conn):
    starting_day = _get_starting_day()

    query = event.select().where(sa.and_(
        event.c.created > starting_day,
        event.c.event_type.in_((EventType.CALLED.value, EventType.NOTIFIED.value)),
    ))

    result = await conn.execute(query)
    events = await result.fetchall()

    data = defaultdict(lambda: defaultdict(int))

    for ev in events:
        day_key = ev.created.strftime(settings.DEFAULT_DATE_FORMAT)
        if ev.event_type == EventType.CALLED.value:
            data[day_key]['called'] += ev.event_count
        elif ev.event_type == EventType.NOTIFIED.value:
            data[day_key]['notified'] += ev.event_count

    return [{
        'date': key,
        'called': value['called'],
        'notified': value['notified'],
    } for key, value in data.items()]
