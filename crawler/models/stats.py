import operator
import statistics

from crawler.helpers import load_config, get_statuses
from crawler.models.bid import (
    get_daily_bids,
    BidType,
    BidStatus,
    ACTIVE_STATUSES,
    GONE_STATUSES,
)
from crawler.models.fund import get_fund, Currency


def get_bare_value_for_bids(bids):
    return sum([b.amount*b.rate for b in bids])


async def get_daily_profit(conn):
    return 500


async def get_current_profit(conn):
    return 700


async def collect_statistics(conn):
    config = await load_config(conn)

    total_profit = await get_daily_profit(conn)
    current_profit = await get_current_profit(conn)
    expected_profit = total_profit * config.CLOSED_BIDS_FACTOR

    fund_uah = sum([
        item.amount for item in await get_fund(conn, currency=Currency.UAH)
    ])

    fund_usd = sum([
        item.amount for item in await get_fund(conn, currency=Currency.USD)
    ])

    fund = {
        Currency.UAH.value: fund_uah,
        Currency.USD.value: fund_usd,
    }

    return {
        'total_profit': total_profit,
        'expected_profit': expected_profit,
        'current_profit': current_profit,
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
