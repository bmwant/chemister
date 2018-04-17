import attr

from utils import get_logger
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
        list(map(lambda x: getattr(x, 'name'), config_trafaret.keys))
    )
    loaded_config = Config(**config_value)
    logger.debug('Loaded config %s', loaded_config)
    return loaded_config
