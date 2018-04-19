"""
Schedule periodic tasks and ensure their execution within given period.
"""
import asyncio

import settings
from utils import LoggableMixin


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
            await self.run_once()
            self.logger.info('Waiting %s seconds to make next update...' %
                             self.interval)
            await asyncio.sleep(self.interval)
            await self.run_daily_tasks()

    async def run_once(self):
        await asyncio.gather(*self.tasks)

    async def run_daily_tasks(self):
        for daily_task in self.daily_tasks:
            if daily_task.is_ready():
                await daily_task

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
        for task in self.tasks:
            await task.close()
