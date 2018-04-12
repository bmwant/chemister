from abc import ABC, abstractmethod


class BaseFetcher(ABC):
    def __init__(self, base_url, *, proxy=None, **kwargs):
        self.base_url = base_url
        self.proxy = proxy

    @abstractmethod
    async def close(self):
        """
        Close open connections and free resources.
        """

    @abstractmethod
    async def request(self, url=None):
        """
        Make a request to remote resource.
        """

    def install_proxy(self, proxy):
        self.proxy = proxy
