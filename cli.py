# -*- coding: utf-8 -*-
import asyncio
import click

from crawler.factory import Factory
from crawler.scheduler import Scheduler
from crawler.helpers import insert_resources
from utils import get_logger


@click.group()
def cli():
    pass


async def schedule_trading(scheduler):
    factory = Factory()
    await factory.init()
    trade_tasks = await factory.create_daily()
    # scheduler.add_tasks(tasks)
    scheduler.add_daily_tasks(trade_tasks)
    try:
        await scheduler.run_forever()
    finally:
        await factory.cleanup()
        await scheduler.cleanup()


@cli.command()
def trade():
    logger = get_logger()
    loop = asyncio.get_event_loop()
    scheduler = Scheduler()
    try:
        loop.run_until_complete(schedule_trading(scheduler))
    except KeyboardInterrupt:
        logger.debug('Trading interrupted...')
    finally:
        # cleanup once again?
        pass


@cli.command()
def check_drivers():
    pass


@cli.command(name='insert_resources')
def insert_resources_command():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(insert_resources())


if __name__ == '__main__':
    cli()
