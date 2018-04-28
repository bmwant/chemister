from aiohttp_session import get_session

from crawler.models.user import get_user_by_id


def login_required(fn):
    async def wrapped(request, *args, **kwargs):
        app = request.app
        logger = app['logger']
        engine = app['db']

        session = await get_session(request)

        if 'user_id' not in session:
            return web.HTTPFound('/auth?redirect_uri={}'.format(request.url))

        user_id = session['user_id']
        async with engine.acquire() as conn:
            user = await get_user_by_id(conn, user_id)

        app['user'] = user
        return await fn(request, *args, **kwargs)

    return wrapped
