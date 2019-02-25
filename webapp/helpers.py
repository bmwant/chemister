import hashlib
import binascii
import secrets
from datetime import datetime
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


async def date_context_processor(request):
    return {
        'now': datetime.now(),
    }


def setup_flash(app):
    app.middlewares.append(flash_middleware)


def create_password(raw_password):
    # todo: give me salt
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        raw_password.encode(),
        b'salt',
        100000,  # number of iterations
    )
    # return hexadecimal string representation of a password hash
    return binascii.hexlify(dk).decode()


def check_password(raw_password, hashed_password_base):
    hashed_password_target = create_password(raw_password)
    return secrets.compare_digest(hashed_password_target, hashed_password_base)
