from aiopg.sa import create_engine

import settings
from crawler.models.bid import bid
from crawler.helpers import load_config


async def get_engine():
    # todo: context manager with closing
    engine = await create_engine(
        settings.DATABASE_DSN,
        minsize=settings.DATABASE_POOL_MINSIZE,
        maxsize=settings.DATABASE_POOL_MAXSIZE,
    )
    return engine


async def go():
    from crawler.models.configs import config as config_model
    engine = await get_engine()
    async with engine.acquire() as conn:
        return list(await conn.execute(config_model.select()))


async def insert_new_bid():
    engine = await get_engine()
    config = await load_config()

    async with engine.acquire() as conn:
        query = bid.insert().values(
            rate='abc',
            amount='',
            currency='',
            phone='',
            dry_run=config.DRY_RUN,
        )
        await conn.execute(query)
