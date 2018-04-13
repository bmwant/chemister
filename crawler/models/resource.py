import attr
from attr.validators import instance_of as an

from .configs import ProxyConfig, FetcherConfig, URLConfig


def ensure_cls(cl):
    def converter(val):
        if isinstance(val, list):
            # Ensure each elem of list is of given class
            return [el if isinstance(el, cl) else cl(**el)
                    for el in val]

        if isinstance(val, cl):
            return val
        else:
            return cl(**val)
    return converter


def list_of(cl):
    def validator(instance, attribute, value):
        if not isinstance(attribute, list):
            return False
        return all([isinstance(el, cl) for el in value])
    return validator


@attr.s
class Resource(object):
    name: str = attr.ib()
    urls = attr.ib(
        default=attr.Factory(list),
        convert=ensure_cls(URLConfig),
        validator=list_of(URLConfig),
    )
    proxy = attr.ib(
        default=ProxyConfig(),
        convert=ensure_cls(ProxyConfig),
        validator=an(ProxyConfig),
    )
    fetcher = attr.ib(
        default=FetcherConfig(),
        convert=ensure_cls(FetcherConfig),
        validator=an(FetcherConfig),
    )
    grabber: str = attr.ib(default='dummy')
    parser: str = attr.ib(default='dummy')
