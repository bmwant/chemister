import attr

from crawler.db import get_engine
from crawler.forms.config import config_trafaret
from crawler.models.configs import config as config_model

from sqlalchemy import desc


async def load_config():
    engine = await get_engine()
    async with engine.acquire() as conn:
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
            list(map(lambda x: getattr(x, 'name'), config_trafaret.keys))
        )
        return Config(**config_value)