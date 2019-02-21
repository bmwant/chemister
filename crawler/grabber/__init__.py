"""
Grab information needed from a resource and store it.
"""
import asyncio
from abc import ABC, abstractmethod

from utils import get_logger
from crawler.models.bid import (
    insert_new_bid,
    mark_bids_as,
    get_daily_bids,
    get_bid_by_signature,
    BidType,
    BidStatus,
    ACTIVE_STATUSES,
)
from crawler.models.resource import Resource


class BaseGrabber(ABC):
    def __init__(self, resource: Resource, *,
                 fetcher=None, parser=None, cache=None, engine=None):
        self.resource = resource
        self.fetcher = fetcher
        self.parser = parser
        self.cache = cache
        self.engine = engine
        self.logger = get_logger(self.__class__.__name__.lower())
        self._exception = None

    def __str__(self):
        return 'Grabber[{}] for resource [{}]'.format(
            self.__class__.__name__, self.name
        )

    @property
    def name(self):
        return self.resource.name

    @property
    def urls(self):
        return self.resource.urls

    def _save_exception(self, fut):
        self._exception = fut.exception()

    def __await__(self):
        fut = asyncio.ensure_future(self.update())
        fut.add_done_callback(self._save_exception)
        return fut.__await__()

    async def close(self):
        self.logger.debug('Closing fetcher connections...')
        await self.fetcher.close()
        self.logger.debug('Closing db engine connections...')
        self.engine.close()
        await self.engine.wait_closed()

    async def update(self):
        data = await self.get_rates()

        if self.cache is not None:
            await self.cache.set(self.name, data)
        print(data)
        # todo: insert rates here for history
        return data

    @abstractmethod
    async def get_rates(self):
        return {}

    async def insert_new_bids(self, bids):
        insert_tasks = []

        async def insert_new_bid_task(*args, **kwargs):
            async with self.engine.acquire() as conn:
                self.logger.debug('Inserting new bid...')
                return await insert_new_bid(conn, *args, **kwargs)

        for bid in bids:
            async with self.engine.acquire() as conn:
                already_stored = await get_bid_by_signature(conn, bid)

            if not already_stored:
                insert_tasks.append(
                    insert_new_bid_task(bid, resource=self.resource))

        await asyncio.gather(*insert_tasks)
