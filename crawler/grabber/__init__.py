"""
Grab information needed from a resource and store it.
"""
from abc import ABC, abstractmethod

from utils import get_logger


class BaseGrabber(ABC):
    def __init__(self, resource, fetcher=None, parser=None, cache=None):
        self.resource = resource
        self.fetcher = fetcher
        self.parser = parser
        self.cache = cache
        self.logger = get_logger(self.__class__.__name__.lower())

    @property
    def name(self):
        return self.resource.name

    @property
    def urls(self):
        return self.resource.urls

    def __await__(self):
        return self.update()

    async def update(self):
        in_bids = await self.get_in_bids()
        out_bids = await self.get_out_bids()
        data = {
            'in_bids': in_bids,
            'out_bids': out_bids,
        }
        if self.cache is not None:
            await self.cache.set(self.name, data)
        return data

    @abstractmethod
    async def get_in_bids(self):
        pass

    @abstractmethod
    async def get_out_bids(self):
        pass

