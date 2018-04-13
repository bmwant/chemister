from crawler.grabber import BaseGrabber


class IUaGrabber(BaseGrabber):
    async def get_in_bids(self):
        data = {}
        for item in self.urls:
            response = await self.fetcher.request(url=item.in_bids)
            currency = item.currency
            currency_data = await self.parser.parse(html=response)
            data[currency] = currency_data
        return data

    async def get_out_bids(self):
        data = {}
        for item in self.urls:
            response = await self.fetcher.request(url=item.out_bids)
            currency = item.currency
            currency_data = await self.parser.parse(html=response)
            data[currency] = currency_data
        return data
