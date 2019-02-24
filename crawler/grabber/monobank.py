from crawler.grabber import BaseGrabber


class MonobankGrabber(BaseGrabber):
    async def get_rates(self):
        data = []
        # todo: get data from database
        return data
