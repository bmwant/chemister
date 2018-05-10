from aiohttp import web

from crawler.forms.config import config_trafaret
from crawler.models.configs import insert_new_config, remove_config
from webapp.helpers import login_required, flash


@login_required
async def save_config(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    data = await request.post()
    value = config_trafaret.check(data)
    logger.info('Saving new config initiated by user %s' % user.email)
    async with engine.acquire() as conn:
        await insert_new_config(conn, new_config=value, user_id=user.id)

    flash(request, 'New config was saved. Using it from this point')
    return web.HTTPFound(router['settings'].url_for())


@login_required
async def delete_config(request):
    app = request.app
    router = app.router
    logger = app['logger']
    engine = app['db']
    user = app['user']

    config_id = request.match_info.get('config_id')
    async with engine.acquire() as conn:
        await remove_config(conn, config_id=config_id)

    flash(request, 'Removed config [#%s]' % config_id)
    return web.HTTPFound(router['settings'].url_for())
