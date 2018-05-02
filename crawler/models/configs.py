import datetime

import attr
import sqlalchemy as sa

from . import metadata
from .user import user


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

    sa.Column('user_id', sa.Integer),

    sa.PrimaryKeyConstraint('id', name='config_id_pkey'),
    sa.ForeignKeyConstraint(['user_id'], [user.c.id],
                            name='config_user_id_fkey',
                            ondelete='NO ACTION'),
)


async def insert_new_config(
    conn,
    *,
    new_config,
    user_id,
):
    return await conn.execute(config.insert().values(
        value=new_config,
        user_id=user_id,
    ))


async def get_config_history(conn):
    result = await conn.execute(config.select())
    return await result.fetchall()
