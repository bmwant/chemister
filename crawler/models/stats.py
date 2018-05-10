import operator
import statistics

from crawler.helpers import load_config
from crawler.models.bid import (
    get_daily_bids,
    BidType,
    BidStatus,
    get_statuses,
    ACTIVE_STATUSES,
    GONE_STATUSES,
)
from crawler.models.fund import get_current_fund_amount, Currency


def get_bare_value_for_bids(bids):
    return sum([b.amount*b.rate for b in bids])


async def get_daily_profit(conn):
    in_bids = await get_daily_bids(conn, bid_type=BidType.IN)
    out_bids = await get_daily_bids(conn, bid_type=BidType.OUT)
    in_value = get_bare_value_for_bids(in_bids)  # we buy
    out_value = get_bare_value_for_bids(out_bids)  # we sell
    return out_value - in_value


async def get_current_profit(conn):
    closed_statuses = [BidStatus.CLOSED]
    in_bids = await get_daily_bids(
        conn,
        bid_type=BidType.IN,
        statuses=closed_statuses,
    )
    out_bids = await get_daily_bids(
        conn,
        bid_type=BidType.OUT,
        statuses=closed_statuses,
    )
    in_value = get_bare_value_for_bids(in_bids)  # we buy all these bids
    out_value = get_bare_value_for_bids(out_bids)  # we sell all these bids
    return out_value - in_value


async def collect_statistics(conn):
    config = await load_config(conn)

    dropped_bids_count = len(await get_daily_bids(conn,
                                                  statuses=GONE_STATUSES))
    closed_statuses = [BidStatus.CLOSED]
    closed_bids_count = len(await get_daily_bids(conn,
                                                 statuses=closed_statuses))
    total_bids_count = len(await get_daily_bids(conn))

    total_profit = await get_daily_profit(conn)
    current_profit = await get_current_profit(conn)
    expected_profit = total_profit * config.CLOSED_BIDS_FACTOR

    fund = {
        Currency.UAH.value: await get_current_fund_amount(conn, Currency.UAH),
        Currency.USD.value: await get_current_fund_amount(conn, Currency.USD),
    }

    return {
        'total_profit': total_profit,
        'expected_profit': expected_profit,
        'current_profit': current_profit,
        'total_bids': total_bids_count,
        'dropped_bids': dropped_bids_count,
        'closed_bids': closed_bids_count,
        'fund': fund,
    }


def _f(func, data):
    if not data:
        return 0
    return func(data)


def get_bids_info(bids):
    rates = list(map(operator.attrgetter('rate'), bids))
    amounts = list(map(operator.attrgetter('amount'), bids))
    statuses = list(map(operator.attrgetter('status'), bids))

    active = _f(len,
                [*filter(lambda s: s in get_statuses(*ACTIVE_STATUSES),
                         statuses)])
    return {
        'active': active,
        'rate': {
            'min': _f(min, rates),
            'avg': _f(statistics.mean, rates),
            'max': _f(max, rates),
        },
        'amount': {
            'min': _f(min, amounts),
            'avg': _f(statistics.mean, amounts),
            'max': _f(max, amounts),
        },
    }
