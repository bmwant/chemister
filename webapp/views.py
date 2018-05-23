import asyncio
from functools import partial

import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session

from crawler.helpers import load_config
from crawler.models.bid import get_daily_bids, BidType
from crawler.models.resource import get_resource_by_id
from crawler.models.phone import get_phones
from crawler.models.user import get_user
from crawler.models.stats import collect_statistics, get_bids_info
from crawler.models.configs import get_config_history
from webapp.utils import refresh_data
from webapp.helpers import login_required, flash, check_password


@login_required
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

    in_info = get_bids_info(in_bids)
    out_info = get_bids_info(out_bids)
    return {
        'in_bids': in_bids,
        'out_bids': out_bids,
        'stats': stats,
        'in_info': in_info,
        'out_info': out_info,
    }


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


@login_required
@aiohttp_jinja2.template('settings.html')
async def settings(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing settings page')

    async with engine.acquire() as conn:
        config = await load_config(conn)
        config_history = await get_config_history(conn)

    return {'config': config, 'history': config_history}


@login_required
@aiohttp_jinja2.template('phones.html')
async def phones(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Accessing phones page')

    async with engine.acquire() as conn:
        phones = await get_phones(conn)

    return {'phones': phones}


@login_required
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


@login_required
@aiohttp_jinja2.template('resource.html')
async def resource(request):
    app = request.app
    logger = app['logger']
    engine = app['db']

    resource_id = request.match_info.get('resource_id')
    logger.info('Accessing resource #%s page' % resource_id)
    async with engine.acquire() as conn:
        resource = await get_resource_by_id(conn, resource_id)

    return {
        'resource': resource
    }


@login_required
@aiohttp_jinja2.template('admin.html')
async def control_panel(request):
    app = request.app
    logger = app['logger']
    engine = app['db']

    logger.info('Accessing admin page')


@login_required
@aiohttp_jinja2.template('operations.html')
async def operations(request):
    app = request.app
    logger = app['logger']
    engine = app['db']

    logger.info('Accessing operations page')


@aiohttp_jinja2.template('login.html')
async def login(request):
    app = request.app
    logger = app['logger']
    engine = app['db']

    logger.info('Accessing login page')


async def do_login(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    form = await request.post()
    email = form['email']
    password = form['password']

    async with engine.acquire() as conn:
        user = await get_user(conn, email)

    if user is None:
        flash(request, 'No user with such email: %s' % email)
        logger.warning('Cannot find user %s', email)
        return web.HTTPFound(router['login'].url_for())

    if not check_password(password, user.password):
        flash(request, 'Incorrect password')
        logger.warning('Wrong password for user %s', email)
        return web.HTTPFound(router['login'].url_for())

    flash(request, 'Successfully logged in')
    session = await get_session(request)
    session['user_id'] = user.id
    return web.HTTPFound(router['index'].url_for())


@login_required
async def logout(request):
    app = request.app
    router = app.router
    logger = app['logger']
    user = app['user']

    session = await get_session(request)
    del session['user_id']
    logger.info('Sign out user %s', user.email)
    flash(request, 'Logged out')
    return web.HTTPFound(router['login'].url_for())
