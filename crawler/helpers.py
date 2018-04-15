import attr

from crawler.db import get_engine
from crawler.models.configs import config as config_model

from sqlalchemy import desc


async def load_config():
    engine = await get_engine()
    async with engine.acquire() as conn:
        result = await conn.execute(
            config_model.select().order_by(desc(config_model.c.created)))
        config_value = (await result.fetchone()).value
        Config = attr.make_class('Config', list(config_value.keys()))
        return Config(**config_value)
