import attr
import sqlalchemy as sa
from attr.validators import instance_of as an

from . import metadata
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


resource = sa.Table(
    'resource', metadata,
    sa.Column('id', sa.Integer),
    sa.Column('name', sa.String),
    sa.Column('url', sa.String),

    sa.PrimaryKeyConstraint('id', name='resource_id_pkey'),
)


async def insert_new_resource(conn, new_resource):
    query = resource.insert().values(
        name=new_resource['name'],
        url=new_resource['link'],
    )
    result = await conn.execute(query)
    return await result.fetchone()


async def get_resource_by_name(conn, resource_name):
    query = resource.select().where(
        resource.c.name == resource_name
    )
    result = await conn.execute(query)
    return await result.fetchone()
