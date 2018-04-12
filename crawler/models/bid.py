import attr


@attr.s
class Bid(object):
    amount: float = attr.ib()
    currency: str = attr.ib()
    rate: float = attr.ib()
    phone: str = attr.ib()
    id: int = attr.ib(default=1)
    date: str = attr.ib(default='17 Apr 2018')
    resource: str = attr.ib(default='i.ua')
