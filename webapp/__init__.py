# -*- coding: utf-8 -*-
import aioredis
import aiopg.sa

import config
from . import views
from . import endpoints


def setup_routes(app):
    app.router.add_get('/', views.index)
    app.router.add_get('/loading', views.loading, name='loading')
    app.router.add_get('/check', views.check_refresh_done)
    app.router.add_get('/settings', views.settings, name='settings')
    app.router.add_post('/save_config', endpoints.save_config)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=config.PROJECT_ROOT / 'static',
                          name='static')
    app.router.add_static('/node_modules/',
                          path=config.PROJECT_ROOT / 'node_modules',
                          name='node_modules')


async def setup_cache(app):
    redis = await aioredis.create_redis(config.REDIS_URI)
    app['cache'] = redis


async def destroy_cache(app):
    redis = app['cache']
    redis.close()
    await redis.wait_closed()


async def init_pg(app):
    engine = await aiopg.sa.create_engine(
        config.DATABASE_DSN,
        minsize=config.DATABASE_POOL_MINSIZE,
        maxsize=config.DATABASE_POOL_MAXSIZE,
        loop=app.loop,
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
