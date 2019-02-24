from crawler.fetcher import BaseFetcher


__all__ = (
    'DummyFetcher',
)


class DummyFetcher(BaseFetcher):
    async def request(self, url=None):
        pass

    async def close(self):
        pass
