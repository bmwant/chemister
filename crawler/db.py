from aiopg.sa import create_engine

import config


async def get_engine():
    # todo: context manager with closing
    engine = await create_engine(
        config.DATABASE_DSN,
        minsize=config.DATABASE_POOL_MINSIZE,
        maxsize=config.DATABASE_POOL_MAXSIZE,
    )
    return engine


async def go():
    from crawler.models.configs import config as config_model
    engine = await get_engine()
    async with engine.acquire() as conn:
        return list(await conn.execute(config_model.select()))

