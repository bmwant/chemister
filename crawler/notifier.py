from operator import attrgetter

from utils import get_logger
from crawler.db import Engine
from crawler.models.bid import (
    get_daily_bids,
    mark_bids_as,
    BidStatus,
)


logger = get_logger(__name__)


async def notify():
    async with Engine() as engine:
        async with engine.acquire() as conn:
            statuses = [BidStatus.NEW]
            daily_bids = await get_daily_bids(conn, statuses=statuses)

            bid_ids = [*map(attrgetter('id'), daily_bids)]
            if bid_ids:
                logger.debug('Notifying bids %s', bid_ids)
                await mark_bids_as(conn, bid_ids, BidStatus.NOTIFIED)
