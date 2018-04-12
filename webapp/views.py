import asyncio
from functools import partial

import aiohttp_jinja2
from aiohttp import web

from webapp.utils import refresh_data


@aiohttp_jinja2.template('index.html')
async def index(request):
    logger = request.app.logger
    logger.info('Accessing index page')



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
