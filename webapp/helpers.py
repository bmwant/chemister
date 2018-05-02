from functools import partial

from aiohttp import web
from aiohttp_session import get_session

import settings
from crawler.models.user import get_user_by_id


# todo: add permission required decorator
def permissions_required(fn):
    async def wrapped(request, *args, **kwargs):
        pass


def login_required(fn):
    async def wrapped(request, *args, **kwargs):
        app = request.app
        router = app.router
        logger = app['logger']
        engine = app['db']

        session = await get_session(request)

        if 'user_id' not in session:
            return web.HTTPFound(router['login'].url_for())

        user_id = session['user_id']
        async with engine.acquire() as conn:
            user = await get_user_by_id(conn, user_id)

        app['user'] = user
        return await fn(request, *args, **kwargs)

    return wrapped


def flash(request, message):
    request[settings.FLASH_REQUEST_KEY].append(message)


def pop_flash(request):
    flash = request[settings.FLASH_REQUEST_KEY]
    request[settings.FLASH_REQUEST_KEY] = []
    return flash


async def flash_middleware(app, handler):
    async def process(request):
        session = await get_session(request)
        flash_incoming = session.get(settings.FLASH_SESSION_KEY, [])
        request[settings.FLASH_REQUEST_KEY] = flash_incoming[:]
        try:
            response = await handler(request)
        finally:
            flash_outgoing = request[settings.FLASH_REQUEST_KEY]
            if flash_outgoing != flash_incoming:
                if flash_outgoing:
                    session[settings.FLASH_SESSION_KEY] = flash_outgoing
                else:
                    del session[settings.FLASH_SESSION_KEY]
        return response

    return process


async def user_context_processor(request):
    return {
        'user': request.app.get('user')
    }


async def flash_context_processor(request):
    return {
        'get_flash': partial(pop_flash, request),
    }
