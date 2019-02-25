import datetime
import csv
import operator
import tempfile

import dateparser
from aiohttp import web, hdrs

import settings
from crawler.models.transaction import (
    remove_transaction,
    set_transaction_status,
    TransactionStatus,
)
from crawler.models.event import add_event, EventType
from webapp.helpers import login_required, flash


@login_required
async def set_transaction_bought(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    t_id = request.match_info.get('t_id')
    logger.info('Confirming transaction #%s bought' % t_id)

    async with engine.acquire() as conn:
        # todo: get or 404
        await set_transaction_status(
            conn,
            t_id=t_id,
            status=TransactionStatus.HANGING,
        )
        # todo: add event?

    flash(request, 'Set bought for transaction [#%s]' % t_id)
    return web.HTTPFound(router['index'].url_for())


@login_required
async def set_transaction_sold(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    t_id = request.match_info.get('t_id')
    logger.info('Confirming transaction #%s sold' % t_id)

    async with engine.acquire() as conn:
        # todo: get or 404
        await set_transaction_status(
            conn,
            t_id=t_id,
            status=TransactionStatus.COMPLETED,
        )
        # todo: add event?

    flash(request, 'Set sold for transaction [#%s]' % t_id)
    return web.HTTPFound(router['index'].url_for())


@login_required
async def delete_transaction(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    t_id = request.match_info.get('t_id')
    async with engine.acquire() as conn:
        await remove_transaction(conn, t_id=t_id)

    flash(request, 'Transaction [#%s] was removed' % t_id)
    return web.HTTPFound(router['index'].url_for())


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
