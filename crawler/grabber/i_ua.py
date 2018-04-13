from crawler.grabber import BaseGrabber


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
        return data

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
        return data
