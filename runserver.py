import os
from functools import partial

import aiohttp
from aiohttp import web

from utils import get_logger
from webapp import (
    setup_routes,
    setup_session,
    setup_templates,
    setup_static_routes,
    setup_cache,
    destroy_cache,
    init_pg,
    close_pg,
)
from webapp.helpers import setup_flash


def run():
    app = web.Application()
    logger = get_logger('webapp')
    app['logger'] = logger
    app.on_startup.append(setup_cache)
    app.on_startup.append(init_pg)
    app.on_shutdown.append(destroy_cache)
    app.on_shutdown.append(close_pg)

    setup_session(app)
    setup_flash(app)
    setup_routes(app)
    setup_static_routes(app)
    setup_templates(app)

    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))

    uprint('Running aiohttp {}'.format(aiohttp.__version__))
    web.run_app(app, print=uprint, port=port)


if __name__ == '__main__':
    run()
