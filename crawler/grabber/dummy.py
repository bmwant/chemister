from crawler.grabber import BaseGrabber


__all__ = (
    'DummyGrabber',
)


class DummyGrabber(BaseGrabber):
    def get_in_bids(self):
        return {}

    def get_out_bids(self):
        return {}
