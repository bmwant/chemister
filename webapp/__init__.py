# -*- coding: utf-8 -*-
import aioredis
import aiopg.sa

import settings
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
                          path=settings.PROJECT_ROOT / 'static',
                          name='static')
    app.router.add_static('/node_modules/',
                          path=settings.PROJECT_ROOT / 'node_modules',
                          name='node_modules')


async def setup_cache(app):
    redis = await aioredis.create_redis(settings.REDIS_URI)
    app['cache'] = redis


async def destroy_cache(app):
    redis = app['cache']
    redis.close()
    await redis.wait_closed()


async def init_pg(app):
    engine = await aiopg.sa.create_engine(
        settings.DATABASE_DSN,
        minsize=settings.DATABASE_POOL_MINSIZE,
        maxsize=settings.DATABASE_POOL_MAXSIZE,
        loop=app.loop,
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
