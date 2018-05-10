"""
Schedule periodic tasks and ensure their execution within given period.
"""
import asyncio
from datetime import datetime
from http import HTTPStatus

import aiohttp

import settings
from utils import make_datetime, LoggableMixin
from crawler.notifier import notify
from crawler.models.bid import _autoclose_bids
from crawler.helpers import get_config


class Scheduler(LoggableMixin):
    def __init__(self, *, tasks=None, daily_tasks=None,
                 interval=settings.DEFAULT_UPDATE_PERIOD):
        self.tasks = tasks or []  # List of grabbers
        # List of tasks to be executed on daily basis
        self.daily_tasks = daily_tasks or []
        self.default_interval = interval
        self.config = None

    def add_tasks(self, tasks: list):
        self.tasks.extend(tasks)

    def add_daily_tasks(self, tasks: list):
        self.daily_tasks.extend(tasks)

    async def update_config(self):
        self.config = await get_config()

    async def run_forever(self):
        # todo: add exceptions handling within child processes
        while True:
            await self.update_config()

            if self.working_time:
                await self.run_tasks()
                await self.run_extra()

            asyncio.ensure_future(self.run_daily_tasks())
            asyncio.ensure_future(self.send_healthcheck())
            self.logger.info('Waiting %s seconds to make next update...' %
                             self.update_interval)
            await asyncio.sleep(self.update_interval)

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

    async def send_healthcheck(self):
        endpoint = settings.HEALTHCHECK_ENDPOINT
        if not endpoint:
            self.logger.info('Healthcheck service is disabled')
            return

        self.logger.debug('Sending healthcheck...')
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as resp:
                if resp.status != HTTPStatus.OK:
                    text = await resp.text()
                    self.logger.error('Request failed %s', text)

    @property
    def update_interval(self):
        interval = self.config.REFRESH_PERIOD_MINUTES or self.default_interval
        # value in minutes
        return interval * 60

    @property
    def working_time(self):
        work_starts = make_datetime(self.config.TIME_DAY_STARTS)
        work_ends = make_datetime(self.config.TIME_DAY_ENDS)
        time_now = datetime.now()
        is_working = work_starts <= time_now <= work_ends
        if not is_working:
            self.logger.debug('s %s, e %s', work_starts, work_ends)
            self.logger.debug(
                'Standby period [%s-%s]: %s' %
                self.config.TIME_DAY_STARTS, self.config.TIME_DAY_ENDS,
                time_now
            )
        return is_working

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
        for task in self.tasks:
            await task.close()
