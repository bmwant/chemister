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
    await factory.init()
    tasks = factory.create()
    scheduler.add_tasks(tasks)
    try:
        await scheduler.run_forever()
    finally:
        await factory.cleanup()
        await scheduler.cleanup()


@cli.command()
def monitor():
    logger = get_logger()
    loop = asyncio.get_event_loop()
    scheduler = Scheduler()
    try:
        loop.run_until_complete(schedule_grabbing(scheduler))
    except KeyboardInterrupt:
        logger.debug('Monitoring interrupted...')


@cli.command()
def check_drivers():
    pass


if __name__ == '__main__':
    cli()
