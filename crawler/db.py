from aiopg.sa import create_engine

import settings


async def get_engine():
    # todo: context manager with closing
    engine = await create_engine(
        settings.DATABASE_DSN,
        minsize=settings.DATABASE_POOL_MINSIZE,
        maxsize=settings.DATABASE_POOL_MAXSIZE,
    )
    return engine
