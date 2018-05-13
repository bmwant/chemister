import datetime
import csv
import operator
import tempfile

import dateparser
from aiohttp import web, hdrs

import settings
from crawler.models.phone import add_new_phone_to_blacklist
from crawler.models.bid import (
    bid,
    BidStatus,
    get_bid_by_id,
    set_bid_status,
    get_bids_for_period,
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


@login_required
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


def _dump_field(field):
    if isinstance(field, bool):
        return int(field)
    elif isinstance(field, datetime.datetime):
        return field.strftime(settings.DEFAULT_DATETIME_FORMAT)
    else:
        return field


@login_required
async def export_to_csv(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    form = await request.post()
    start_date = dateparser.parse(form['day_start'])
    datetime_day_end = dateparser.parse(form['day_end'])
    end_date = datetime_day_end + datetime.timedelta(days=1)
    logger.debug('Exporting bids for period %s - %s', start_date, end_date)
    async with engine.acquire() as conn:
        bids = await get_bids_for_period(
            conn,
            start_date=start_date,
            end_date=end_date,
        )

    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        writer = csv.writer(f)
        header = [*map(operator.attrgetter('name'), bid.columns)]
        writer.writerow(header)
        for b in bids:
            writer.writerow([_dump_field(getattr(b, prop)) for prop in header])

    start_date_str = start_date.strftime('%d-%m-%y')
    end_date_str = datetime_day_end.strftime('%d-%m-%y')
    filename = 'exported_bids_{}_{}.csv'.format(start_date_str, end_date_str)

    return web.FileResponse(path=f.name, headers={
        hdrs.CONTENT_DISPOSITION: 'inline; filename="{}"'.format(filename)
    })
