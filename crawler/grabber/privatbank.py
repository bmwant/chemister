from crawler.grabber import BaseGrabber


class PrivatbankGrabber(BaseGrabber):
    async def get_rates(self):
        data = []
        for item in self.urls:
            self.logger.debug(
                'Grabbing %(currency)s rates for %(name)s',
                dict(currency=item.currency, name=self.name)
            )
            response = await self.fetcher.request(url=item.url, is_json=True)
            data.extend(response)
        # currency = item.currency
        # currency_data = self.parser.parse(html=response)
        return data
