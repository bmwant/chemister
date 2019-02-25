import asyncio
from functools import partial

import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session

from crawler.helpers import load_config
from crawler.models.transaction import (
    get_transactions,
    TransactionStatus,
    UNCONFIRMED_STATUSES,
)
from crawler.models.resource import get_resource_by_id
from crawler.models.rate import get_rates
from crawler.models.user import get_user
from crawler.models.stats import collect_statistics, get_bids_info
from crawler.models.configs import get_config_history
from crawler.models.fund import get_investments
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
        unconfirmed = await get_transactions(
            conn,
            statuses=UNCONFIRMED_STATUSES,
        )
        hanging = await get_transactions(
            conn,
            statuses=[TransactionStatus.HANGING],
        )
        completed = await get_transactions(
            conn,
            statuses=[TransactionStatus.COMPLETED],
        )
        stats = {
            'total_profit': 0,
            'expected_profit': 0,
            'current_profit': 0,
            'fund': {'USD': 0, 'UAH': 0},
        }

    return {
        'unconfirmed': unconfirmed,
        'hanging': hanging,
        'completed': completed,
        'stats': stats,
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
@aiohttp_jinja2.template('investments.html')
async def investments(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    
    logger.info('Accessing investment page')

    async with engine.acquire() as conn:
        investments = await get_investments(conn)

    return {
        'investments': investments, 
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


@aiohttp_jinja2.template('rates.html')
async def rates(request):
    app = request.app
    logger = app['logger']
    engine = app['db']

    async with engine.acquire() as conn:
        rates = await get_rates(conn)

    logger.info('Accessing rates archive page')
    return {
        'rates': rates,
    }


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
