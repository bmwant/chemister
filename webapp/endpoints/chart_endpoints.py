from aiohttp import web

from crawler.models.charts import (
    get_profit_last_month,
    get_bids_statuses_last_month,
    get_notifications_last_month,
)


async def get_daily_profit_month(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    async with engine.acquire() as conn:
        data = await get_profit_last_month(conn)

    return web.json_response(data=data)


async def get_bid_statuses_month(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    async with engine.acquire() as conn:
        data = await get_bids_statuses_last_month(conn)

    return web.json_response(data=data)


async def get_notifications_month(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']

    async with engine.acquire() as conn:
        data = await get_notifications_last_month(conn)

    return web.json_response(data=data)
