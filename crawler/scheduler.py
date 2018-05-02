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

    def add_tasks(self, tasks: list):
        self.tasks.extend(tasks)

    def add_daily_tasks(self, tasks: list):
        self.daily_tasks.extend(tasks)

    async def run_forever(self):
        # todo: add exceptions handling within child processes
        while True:
            is_working = await self.working_time
            if is_working:
                await self.run_tasks()
                await self.run_extra()

            # todo: call soon without blocking
            await self.run_daily_tasks()
            await self.send_healthcheck()
            interval = await self._get_update_interval()
            self.logger.info('Waiting %s seconds to make next update...' %
                             interval)
            await asyncio.sleep(interval)

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

    async def _get_update_interval(self):
        config = await get_config()
        interval = config.REFRESH_PERIOD_MINUTES or self.default_interval
        # value in minutes
        return interval * 60

    @property
    async def working_time(self):
        config = await get_config()
        work_starts = make_datetime(config.TIME_DAY_STARTS)
        work_ends = make_datetime(config.TIME_DAY_ENDS)
        time_now = datetime.now()
        is_working = work_starts <= time_now <= work_ends
        if not is_working:
            self.logger.debug('s %s, e %s', work_starts, work_ends)
            self.logger.debug(
                'Standby period [%s-%s]: %s' %
                config.TIME_DAY_STARTS, config.TIME_DAY_ENDS, time_now
            )
        return is_working

    async def cleanup(self):
        self.logger.info('Cleaning up resources...')
        for task in self.tasks:
            await task.close()
