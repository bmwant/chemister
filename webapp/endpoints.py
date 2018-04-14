from aiohttp import web

from crawler.models.configs import config as config_model
from crawler.forms.config import config_trafaret


async def save_config(request):
    db = request.app['db']
    data = await request.post()
    value = config_trafaret.check(data)
    async with db.acquire() as conn:
        await conn.execute(config_model.insert().values(
            value=value,
        ))

    return web.HTTPFound('/settings')


