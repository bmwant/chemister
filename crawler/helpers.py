import attr

from utils import get_logger
from crawler.db import Engine
from crawler.forms.config import config_trafaret
from crawler.models.configs import config as config_model

from sqlalchemy import desc


logger = get_logger(__name__)


async def load_config(conn):
    result = await conn.execute(
        config_model.select().order_by(desc(config_model.c.created)))

    row = await result.fetchone()
    if row is None:
        raise RuntimeError(
            'Improperly configured. '
            'Your database must contain at least one config value'
        )

    config_value = row.value
    Config = attr.make_class(
        'Config',
        {key.name: attr.ib(default=None) for key in config_trafaret.keys}
    )
    loaded_config = Config(**config_value)
    return loaded_config


async def get_config():
    """
    A wrapper to load config in case you do not have any created engine you can
    bind to.
    """
    async with Engine() as engine:
        async with engine.acquire() as conn:
            return await load_config(conn)
