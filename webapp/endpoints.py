from aiohttp import web

from crawler.forms.config import config_trafaret
from crawler.models.configs import insert_new_config


async def save_config(request):
    data = await request.post()
    value = config_trafaret.check(data)
    await insert_new_config(value)

    return web.HTTPFound('/settings')


