"""
Schedule periodic tasks and ensure their execution within given period.
"""
import asyncio

import settings
from utils import get_logger, get_minutes_value


class Scheduler(object):
    def __init__(self, tasks=None, interval=settings.UPDATE_PERIOD):
        self.tasks = tasks or []  # List of grabbers
        self.interval = interval
        self.logger = get_logger(self.__class__.__name__.lower())
        self.daily_tasks = []

    def add_tasks(self, tasks: list):
        self.tasks.extend(tasks)

    def add_daily_task(self, task):
        self.daily_tasks.append(task)

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
                await daily_task()

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
        for task in self.tasks:
            await task.close()


class ScheduledTask(object):
    def __init__(self, task, scheduled_time):
        self.task = task
        self.scheduled_time = scheduled_time
        self.done = False

    def is_ready(self):
        return not self.done

    def __await__(self):
        # Early, to prevent double launching
        self.done = True
        return self.task()
