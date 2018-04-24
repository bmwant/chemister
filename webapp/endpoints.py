from aiohttp import web

from crawler.forms.config import config_trafaret
from crawler.models.configs import insert_new_config
from crawler.models.phone import add_new_phone_to_blacklist
from crawler.models.bid import (
    BidStatus,
    get_bid_by_id,
    set_bid_status,
)


async def save_config(request):
    app = request.app
    logger = app['logger']
    engine = app['db']
    logger.info('Saving new config')

    data = await request.post()
    value = config_trafaret.check(data)
    async with engine.acquire() as conn:
        await insert_new_config(conn, value)

    return web.HTTPFound('/settings')


async def set_bid_called(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    bid_id = request.match_info.get('bid_id')
    logger.info('Marking bid #%s as called' % bid_id)

    async with engine.acquire() as conn:
        result = await set_bid_status(
            conn,
            bid_id=bid_id,
            bid_status=BidStatus.CALLED,
        )

    return web.HTTPFound(router['index'].url_for())


async def set_bid_rejected(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    bid_id = request.match_info.get('bid_id')
    logger.info('Marking bid #%s as rejected' % bid_id)

    async with engine.acquire() as conn:
        result = await set_bid_status(
            conn,
            bid_id=bid_id,
            bid_status=BidStatus.REJECTED,
        )

    return web.HTTPFound(router['index'].url_for())


async def set_bid_closed(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    bid_id = request.match_info.get('bid_id')
    logger.info('Marking bid #%s as closed' % bid_id)

    async with engine.acquire() as conn:
        result = await set_bid_status(
            conn,
            bid_id=bid_id,
            bid_status=BidStatus.CLOSED,
        )

    return web.HTTPFound(router['index'].url_for())


async def ban_bid_phone(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    bid_id = request.match_info.get('bid_id')

    async with engine.acquire() as conn:
        bid = await get_bid_by_id(conn, bid_id)
        logger.info('Adding phone %s to blacklist' % bid.phone)
        await add_new_phone_to_blacklist(
            conn,
            phone_number=bid.phone,
            reason='Вони дебіли',
        )

    return web.HTTPFound(router['phones'].url_for())
