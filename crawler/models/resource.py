import attr
from attr.validators import instance_of as an


def ensure_cls(cl):
    def converter(val):
        if isinstance(val, cl):
            return val
        else:
            return cl(**val)
    return converter


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
class Resource(object):
    name: str = attr.ib()
    url: str = attr.ib()
    proxy = attr.ib(default=ProxyConfig(),
                    convert=ensure_cls(ProxyConfig),
                    validator=an(ProxyConfig))
    fetcher = attr.ib(default=FetcherConfig(),
                      convert=ensure_cls(FetcherConfig),
                      validator=an(FetcherConfig))
    parser: str = attr.ib(default='dummy')
