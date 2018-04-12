"""
Schedule periodic tasks and ensure their execution within given period.
"""
import asyncio

import config
from utils import get_logger


class Scheduler(object):
    def __init__(self, tasks=None, interval=config.UPDATE_PERIOD):
        self.tasks = tasks or []
        self.interval = interval
        self.logger = get_logger(self.__class__.__name__.lower())

    def add_tasks(self, tasks: list):
        self.tasks.extend(tasks)

    async def run_forever(self):
        # todo: add exceptions handling within child processes
        while True:
            await self.run_once()
            self.logger.info('Waiting %s seconds to make next update...' %
                             self.interval)
            await asyncio.sleep(self.interval)

    async def run_once(self):
        await asyncio.gather(*self.tasks)

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
