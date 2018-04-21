"""
Schedule periodic tasks and ensure their execution within given period.
"""
import asyncio
from datetime import datetime

import settings
from utils import make_datetime, LoggableMixin

from crawler.notifier import notify
from crawler.models.bid import _autoclose_bids
from crawler.helpers import get_config


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
            if self.working_time:
                await self.run_tasks()
                await self.run_extra()

            # todo: call soon without blocking
            await self.run_daily_tasks()
            self.logger.info('Waiting %s seconds to make next update...' %
                             self.interval)
            await asyncio.sleep(self.interval)

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

    @property
    async def working_time(self):
        config = await get_config()
        work_starts = make_datetime(config.TIME_DAY_STARTS)
        work_ends = make_datetime(config.TIME_DAY_ENDS)
        time_now = datetime.now()
        return work_starts <= time_now <= work_ends

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
        for task in self.tasks:
            await task.close()
