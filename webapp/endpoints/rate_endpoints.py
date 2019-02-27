from aiohttp import web, hdrs

import settings
from crawler.models.rate import (
    insert_new_rate,
)
from crawler.models.event import add_event, EventType
from webapp.helpers import login_required, flash


@login_required
async def add_new_rate(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    form = await request.post()
    bank = form['bank']
    rate_buy = form['rate_buy']
    rate_sale = form['rate_sale']

    logger.info('Inserting new rate item for %s' % bank)

    async with engine.acquire() as conn:
        rate_id = await insert_new_rate(
            conn,
            bank=bank,
            rate_buy=rate_buy,
            rate_sale=rate_sale,
        )
        # todo: add event?

    flash(request, 'Inserted new rate item [#%s]' % rate_id)
    return web.HTTPFound(router['rates'].url_for())
