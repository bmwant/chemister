import asyncio
from functools import partial

import aiohttp_jinja2
from aiohttp import web

from crawler.helpers import load_config
from crawler.models.bid import get_daily_bids, BidType
from crawler.models.stats import collect_statistics
from webapp.utils import refresh_data, load_resources, get_cached_value


@aiohttp_jinja2.template('index.html')
async def index(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing index page')

    async with engine.acquire() as conn:
        in_bids = await get_daily_bids(conn, bid_type=BidType.IN)
        out_bids = await get_daily_bids(conn, bid_type=BidType.OUT)
        stats = await collect_statistics(conn)

    return {
        'in_bids': in_bids,
        'out_bids': out_bids,
        'stats': stats,
    }


async def get_bids_from_cache(cache):
    # cache = request.app['cache']
    resources = await load_resources()
    in_bids = []
    out_bids = []
    for resource in resources:
        resource_data = await get_cached_value(cache=cache,
                                               key=resource)
        if resource_data is not None:
            in_bids.extend(resource_data['in_bids'])
            out_bids.extend(resource_data['out_bids'])


@aiohttp_jinja2.template('loading.html')
async def loading(request):
    app = request.app
    logger = app['logger']
    logger.info('Accessing loading page')
    task = getattr(app, 'refreshing', None)
    if task is None:
        task = asyncio.ensure_future(refresh_data())
        callback = partial(done_refresh, app)
        task.add_done_callback(callback)
        app.refreshing = task


def done_refresh(app, future):
    logger = app['logger']
    if hasattr(app, 'refreshing'):
        del app.refreshing

    exc = future.exception()
    if exc is not None:
        logger.critical('Failed to update: %s', exc)


async def check_refresh_done(request):
    return web.json_response({
        'refreshing': hasattr(request.app, 'refreshing')
    })


@aiohttp_jinja2.template('settings.html')
async def settings(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing settings page')

    async with engine.acquire() as conn:
        config = await load_config(conn)

    return {'config': config}


@aiohttp_jinja2.template('phones.html')
async def phones(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing phones page')

    async with engine.acquire() as conn:
        config = await load_config(conn)

    return {'config': config}


@aiohttp_jinja2.template('statistics.html')
async def statistics(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing statistics page')

    async with engine.acquire() as conn:
        stats = await collect_statistics(conn)

    return {
        'stats': stats
    }


@aiohttp_jinja2.template('resource.html')
async def resource(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing resource page')
