"""
Schedule periodic tasks and ensure their execution within given period.
"""
import asyncio

import settings
from utils import LoggableMixin

from crawler.notifier import notify
from crawler.models.bid import _autoclose_bids


class Scheduler(LoggableMixin):
    def __init__(self, *, tasks=None, daily_tasks=None,
                 interval=settings.UPDATE_PERIOD):
        self.tasks = tasks or []  # List of grabbers
        # List of tasks to be executed on daily basis
        self.daily_tasks = daily_tasks or []
        self.interval = interval

    def add_tasks(self, tasks: list):
        self.tasks.extend(tasks)

    def add_daily_tasks(self, tasks: list):
        self.daily_tasks.extend(tasks)

    async def run_forever(self):
        # todo: add exceptions handling within child processes
        while True:
            await self.run_tasks()
            await self.run_extra()
            self.logger.info('Waiting %s seconds to make next update...' %
                             self.interval)
            await asyncio.sleep(self.interval)
            # todo: call soon without blocking
            await self.run_daily_tasks()

    async def run_tasks(self):
        """
        Run grabber tasks which are executed in parallel for each resource.
        """
        await asyncio.gather(*self.tasks)

    async def run_extra(self):
        """
        Run extra tasks which depend on data received from tasks.
        """

        self.logger.debug('Sending sms to every new bid owner...')
        await notify()
        self.logger.debug('Closing all bids with their owners...')
        await _autoclose_bids()

    async def run_daily_tasks(self):
        for daily_task in self.daily_tasks:
            if daily_task.is_ready():
                await daily_task

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
        for task in self.tasks:
            await task.close()
