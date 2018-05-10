from aiohttp import web


from crawler.models.phone import add_new_phone_to_blacklist
from crawler.models.bid import (
    BidStatus,
    get_bid_by_id,
    set_bid_status,
)
from crawler.models.event import add_event, EventType

from webapp.helpers import login_required, flash


async def set_bid_called(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    bid_id = request.match_info.get('bid_id')
    logger.info('Marking bid #%s as called' % bid_id)

    async with engine.acquire() as conn:
        # todo: get or 404
        bid = await get_bid_by_id(conn, bid_id)
        await set_bid_status(
            conn,
            bid_id=bid_id,
            bid_status=BidStatus.CALLED,
        )
        await add_event(
            conn,
            event_type=EventType.CALLED,
            description='Called %s' % bid.phone,
            user_id=user.id,
        )

    flash(request, 'Called %s for bid [#%s]' % (bid.phone, bid_id))
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


@login_required
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
