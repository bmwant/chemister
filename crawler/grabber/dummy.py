from crawler.grabber import BaseGrabber


__all__ = (
    'DummyGrabber',
)


class DummyGrabber(BaseGrabber):
    async def get_in_bids(self):
        return []

    async def get_out_bids(self):
        return []
