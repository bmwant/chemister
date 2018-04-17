import datetime

import attr
import sqlalchemy as sa

from . import metadata


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


config = sa.Table(
    'config', metadata,
    sa.Column('id', sa.Integer),
    sa.Column('created', sa.DateTime, default=datetime.datetime.now),
    sa.Column('value', sa.JSON),

    sa.PrimaryKeyConstraint('id', name='config_id_pkey'),
)


async def insert_new_config(conn, new_config):
    return await conn.execute(config.insert().values(
        value=new_config,
    ))
