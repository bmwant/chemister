"""
Grab information needed from a resource and store it.
"""
from utils import get_logger


# todo: implement actual navigation
# note: implementation is straightforward: just find desired text and lookup
# closest link to it. Repeat procedure until mark is found on a page.
NAVIGATE_MAP = {
    'William Hill': 'http://sports.williamhill.com/bet/en-gb/betting/e/12085242/World+Cup+2018+-+Outright.html',
    'Paddy Power': 'https://www.paddypower.com/football/2018-fifa-world-cup?tab=outrights',
    'Sky Bet': 'https://m.skybet.com/football/world-cup-2018/event/16742642',
    'bet365': 'https://mobile.bet365.com',
}


class Grabber(object):
    def __init__(self, name, fetcher=None, parser=None, cache=None):
        self.name = name
        self.fetcher = fetcher
        self.parser = parser
        self.cache = cache
        self.logger = get_logger(self.__class__.__name__.lower())

    def __await__(self):
        return self.update()

    async def update(self):
        # it's a lazy function called just once
        target_url = await self.navigate()
        response = await self.fetcher.request(url=target_url)
        data = self.parser.parse(response)
        if self.cache is not None:
            await self.cache.set(self.name, data)
        return data

    async def navigate(self):
        """
        Explore resource to find a page from which to grab data
        """
        url = NAVIGATE_MAP[self.name]
        self.fetcher.base_url = url
