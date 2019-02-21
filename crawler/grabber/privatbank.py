import operator

import settings
from crawler.grabber import BaseGrabber
from crawler.filters import Container, Filter
from crawler.helpers import load_config


class PrivatbankGrabber(BaseGrabber):
    async def get_rates(self):
        for item in self.urls:
            self.logger.debug(
                'Grabbing %(currency)s rates for %(name)s',
                dict(currency=item.currency, name=self.name)
            )
            response = await self.fetcher.request(url=item.url, is_json=True)
        # currency = item.currency
        # currency_data = self.parser.parse(html=response)
        return response
