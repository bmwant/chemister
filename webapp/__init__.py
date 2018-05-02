# -*- coding: utf-8 -*-
import base64

import jinja2
import aioredis
import aiopg.sa
import aiohttp_jinja2
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

import settings
from . import views
from . import endpoints
from . import filters
from . import helpers


def setup_routes(app):
    app.router.add_get('/', views.index, name='index')
    app.router.add_get('/loading', views.loading, name='loading')
    app.router.add_get('/check', views.check_refresh_done)
    app.router.add_get('/settings', views.settings, name='settings')
    app.router.add_get('/statistics', views.statistics, name='statistics')
    app.router.add_get('/phones', views.phones, name='phones')
    app.router.add_get('/admin', views.control_panel, name='admin')
    app.router.add_get('/login', views.login, name='login')
    app.router.add_post('/do_login', views.do_login)
    app.router.add_get('/logout', views.logout)

    app.router.add_post('/save_config', endpoints.save_config)

    # bid
    # todo: make post and ajax
    app.router.add_get('/bid/set_closed/{bid_id}', endpoints.set_bid_closed)
    app.router.add_get('/bid/set_called/{bid_id}', endpoints.set_bid_called)
    app.router.add_get('/bid/set_rejected/{bid_id}',
                       endpoints.set_bid_rejected)
    app.router.add_get('/bid/ban_phone/{bid_id}', endpoints.ban_bid_phone)

    # resource
    app.router.add_get('/resource/{resource_id}', views.resource)

    # charts
    app.router.add_get('/charts/get_profit_month',
                       endpoints.get_daily_profit_month)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=settings.PROJECT_ROOT / 'static',
                          name='static')
    app.router.add_static('/node_modules/',
                          path=settings.PROJECT_ROOT / 'node_modules',
                          name='node_modules')


def setup_templates(app):
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(settings.TEMPLATES_DIR)),
        filters={
            'checkbox': filters.checkbox,
            'format_time': filters.format_time,
            'format_datetime': filters.format_datetime,
        },
        context_processors=(
            helpers.flash_context_processor,
            helpers.user_context_processor,
        )
    )


def setup_session(app):
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))


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
