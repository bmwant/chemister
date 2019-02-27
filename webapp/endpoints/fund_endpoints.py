from aiohttp import web

import settings
from crawler.helpers import get_enum_by_value
from crawler.models.fund import (
    insert_new_investment,
    Currency,
)
from crawler.models.event import add_event, EventType
from webapp.helpers import login_required, flash


@login_required
async def add_new_investment(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    form = await request.post()
    amount = float(form['amount'])
    currency = get_enum_by_value(Currency, value=form['currency'])
    bank = form['bank']

    logger.info('Adding new investment for user %s' % user.email)

    async with engine.acquire() as conn:
        investment_id = await insert_new_investment(
            conn,
            amount=amount,
            currency=currency,
            bank=bank,
            user_id=user.id,
        )
        # todo: add event?

    flash(request, 'Investment [#%d] of %.2f added for user %s' % (
        investment_id, amount, user.email))
    return web.HTTPFound(router['investments'].url_for())
