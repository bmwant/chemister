import asyncio
from functools import partial

import aiohttp_jinja2
from aiohttp import web

from webapp.utils import refresh_data, load_resources, get_cached_value
from crawler.models.configs import config as config_model


@aiohttp_jinja2.template('index.html')
async def index(request):
    logger = request.app.logger
    cache = request.app['cache']
    logger.info('Accessing index page')
    resources = await load_resources()

    in_bids = []
    out_bids = []
    for resource in resources:
        resource_data = await get_cached_value(cache=cache,
                                               key=resource)
        if resource_data is not None:
            in_bids.extend(resource_data['in_bids'])
            out_bids.extend(resource_data['out_bids'])

    return {
        'in_bids': in_bids,
        'out_bids': out_bids,
    }


@aiohttp_jinja2.template('loading.html')
async def loading(request):
    app = request.app
    logger = app.logger
    logger.info('Accessing loading page')
    task = getattr(app, 'refreshing', None)
    if task is None:
        task = asyncio.ensure_future(refresh_data())
        callback = partial(done_refresh, app)
        task.add_done_callback(callback)
        app.refreshing = task


def done_refresh(app, future):
    logger = app.logger
    if hasattr(app, 'refreshing'):
        del app.refreshing

    exc = future.exception()
    if exc is not None:
        logger.critical('Failed to update: %s', exc)


async def check_refresh_done(request):
    return web.json_response({
        'refreshing': hasattr(request.app, 'refreshing')
    })


@aiohttp_jinja2.template('form.html')
async def settings(request):
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(config_model.select())
        items = await cursor.fetchall()
        # questions = [dict(q) for q in records]
        # return {'questions': questions}
        print(items)
        return {}
