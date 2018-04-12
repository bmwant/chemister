# -*- coding: utf-8 -*-
import asyncio
import click

from crawler.factory import Factory
from crawler.scheduler import Scheduler
from utils import get_logger


@click.group()
def cli():
    pass


async def schedule_grabbing(scheduler):
    factory = Factory()
    await factory.init_cache()
    factory.load_resources()
    factory.load_teams()
    tasks = factory.create()
    scheduler.add_tasks(tasks)
    await scheduler.run_forever()


@cli.command()
def monitor():
    logger = get_logger()
    loop = asyncio.get_event_loop()
    scheduler = Scheduler()
    try:
        loop.run_until_complete(schedule_grabbing(scheduler))
    except KeyboardInterrupt:
        logger.debug('Interrupt monitoring...')
    finally:
        loop.run_until_complete(scheduler.cleanup())


@cli.command()
def check_drivers():
    pass


if __name__ == '__main__':
    cli()
