"""
Grab information needed from a resource and store it.
"""
import asyncio
from abc import ABC, abstractmethod

from utils import get_logger
from crawler.models.bid import (
    insert_new_bid,
    mark_inactive,
    get_daily_bids,
    get_bid_by_signature,
    BidType,
)


class BaseGrabber(ABC):
    def __init__(self, resource, *,
                 fetcher=None, parser=None, cache=None, engine=None):
        self.resource = resource
        self.fetcher = fetcher
        self.parser = parser
        self.cache = cache
        self.engine = engine
        self.logger = get_logger(self.__class__.__name__.lower())

    @property
    def name(self):
        return self.resource.name

    @property
    def urls(self):
        return self.resource.urls

    def __await__(self):
        return self.update()

    async def close(self):
        self.logger.debug('Closing fetcher connections...')
        await self.fetcher.close()
        self.logger.debug('Closing db engine connections...')
        self.engine.close()
        await self.engine.wait_closed()

    async def update(self):
        in_bids = await self.get_in_bids()
        out_bids = await self.get_out_bids()
        data = {
            'in_bids': in_bids,
            'out_bids': out_bids,
        }
        if self.cache is not None:
            await self.cache.set(self.name, data)

        in_bids_data = map(lambda b: self._set_bid_type(b, BidType.IN),
                           in_bids)
        out_bids_data = map(lambda b: self._set_bid_type(b, BidType.OUT),
                            out_bids)

        fetched_bids = [*in_bids_data, *out_bids_data]
        await self.mark_inactive_bids(fetched_bids)

        await self.insert_new_bids(fetched_bids)
        return data

    @abstractmethod
    async def get_in_bids(self):
        return []

    @abstractmethod
    async def get_out_bids(self):
        return []

    @staticmethod
    def _set_bid_type(bid: dict, bid_type: BidType):
        bid['bid_type'] = bid_type.value
        return bid

    @staticmethod
    def _not_in(bid, fetched_bids: list):
        bid_signature = {
            'rate': bid.rate,
            'amount': bid.amount,
            'phone': bid.phone,
            'currency': bid.currency,
            'bid_type': bid.bid_type,
        }
        return bid_signature not in fetched_bids

    async def mark_inactive_bids(self, fetched_bids):
        async with self.engine.acquire() as conn:
            daily_in_bids = await get_daily_bids(conn, BidType.IN)
            daily_out_bids = await get_daily_bids(conn, BidType.OUT)
            daily_bids = [*daily_in_bids, *daily_out_bids]
            inactive_bids = [b.id for b in daily_bids
                             if self._not_in(b, fetched_bids)]
            self.logger.warning('Marking bids as inactive %s', inactive_bids)
            await mark_inactive(conn, inactive_bids)

    async def insert_new_bids(self, bids):
        resource = None
        insert_tasks = []
        # todo: check acquiring with gather
        async with self.engine.acquire() as conn:
            for bid in bids:
                already_stored = await get_bid_by_signature(conn, bid)
                if not already_stored:
                    insert_tasks.append(
                        insert_new_bid(conn, bid, resource=resource))

            await asyncio.gather(*insert_tasks)
