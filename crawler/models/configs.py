import attr


@attr.s
class FetcherConfig(object):
    driver: str = attr.ib(default=None)
    instance: str = attr.ib(default='simple')


@attr.s
class ProxyConfig(object):
    ip: str = attr.ib(default=None)
    use: bool = attr.ib(default=False)
    port: int = attr.ib(default=80)


@attr.s
class URLConfig(object):
    currency: str = attr.ib(default=None)
    in_bids: str = attr.ib(default=None)
    out_bids: str = attr.ib(default=None)
