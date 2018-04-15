import os
from functools import partial

import jinja2
import aiohttp
import aiohttp_jinja2
from aiohttp import web

import settings
from utils import get_logger
from webapp import (
    setup_routes,
    setup_static_routes,
    setup_cache,
    destroy_cache,
    init_pg,
    close_pg,
)
from webapp.filters import checkbox


def run():
    app = web.Application()
    logger = get_logger('webapp')
    app.logger = logger
    app.on_startup.append(setup_cache)
    app.on_startup.append(init_pg)
    app.on_shutdown.append(destroy_cache)
    app.on_shutdown.append(close_pg)
    setup_routes(app)
    setup_static_routes(app)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(settings.TEMPLATES_DIR)),
        filters={'checkbox': checkbox},
    )

    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))

    uprint('Running aiohttp {}'.format(aiohttp.__version__))
    web.run_app(app, print=uprint, port=port)


if __name__ == '__main__':
    run()
