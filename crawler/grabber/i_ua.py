import operator

from crawler.grabber import BaseGrabber
from crawler.filters import Container, Filter
from crawler.helpers import load_config


class IUaGrabber(BaseGrabber):
    async def get_in_bids(self):
        data = []
        for item in self.urls:
            self.logger.debug(
                'Grabbing IN %(currency)s bids for %(name)s',
                dict(currency=item.currency, name=self.name)
            )
            response = await self.fetcher.request(url=item.in_bids)
            # currency = item.currency
            currency_data = self.parser.parse(html=response)
            data.extend(currency_data)
        return await self.filter_data(data)

    async def get_out_bids(self):
        data = []
        for item in self.urls:
            self.logger.debug(
                'Grabbing OUT %(currency)s bids for %(name)s',
                dict(currency=item.currency, name=self.name)
            )
            response = await self.fetcher.request(url=item.out_bids)
            # currency = item.currency
            currency_data = self.parser.parse(html=response)
            data.extend(currency_data)
        return await self.filter_data(data)

    async def filter_data(self, data):
        async with self.engine.acquire() as conn:
            config = await load_config(conn)

        filtered_result = Container(data) >> \
            Filter('amount', operator.ge, config.MIN_BID_AMOUNT) >> \
            Filter('amount', operator.le, config.MAX_BID_AMOUNT)

        self.logger.info('Fetched: %s. Filter applied: %s',
                         len(data), len(filtered_result))

        return filtered_result.data
