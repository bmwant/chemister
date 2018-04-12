import asyncio
from functools import partial

import aiohttp_jinja2
from aiohttp import web

from webapp.utils import (
    load_teams,
    load_resources,
    get_cached_value,
    refresh_data,
)


@aiohttp_jinja2.template('index.html')
async def index(request):
    logger = request.app.logger
    logger.info('Accessing index page')
    cache = request.app['cache']

    teams = await load_teams()
    available_resources = await load_resources()

    resources = {}
    has_data = False
    for resource in available_resources:
        resource_data = await get_cached_value(cache=cache,
                                               key=resource)
        if resource_data is not None:
            has_data = True
        resources[resource] = resource_data

    if not has_data:
        loading_url = request.app.router['loading'].url_for()
        return web.HTTPFound(loading_url)

    return {
        'teams': teams,
        'resources': resources
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
