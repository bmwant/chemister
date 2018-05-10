import asyncio
from unittest import mock
from datetime import datetime, timedelta

import attr
import pytest

import settings
from crawler.grabber import BaseGrabber
from crawler.scheduler import Scheduler
from crawler.scheduled_task import ScheduledTask


@pytest.mark.run_loop
async def test_daily_tasks():
    scheduler = Scheduler()

    async def dummy_task():
        print('Running dummy task...')
        await asyncio.sleep(0.1)

    task = ScheduledTask(task=dummy_task, scheduled_time='23:45')
    scheduler.add_daily_tasks([task])

    task.is_ready = lambda: True
    await scheduler.run_daily_tasks()
    assert task.done


async def _get_config_mock():
    _Config = attr.make_class(
        'Config',
        ['TIME_DAY_STARTS', 'TIME_DAY_ENDS', 'REFRESH_PERIOD_MINUTES'],
    )
    datetime_starts = datetime.now() - timedelta(hours=1)
    time_starts = datetime_starts.strftime(settings.DEFAULT_TIME_FORMAT)
    datetime_ends = datetime.now() + timedelta(hours=1)
    time_ends = datetime_ends.strftime(settings.DEFAULT_TIME_FORMAT)

    _config = _Config(
        TIME_DAY_STARTS=time_starts,
        TIME_DAY_ENDS=time_ends,
        REFRESH_PERIOD_MINUTES=0.1,
    )
    return _config


@pytest.mark.run_loop
async def test_working_time():
    scheduler = Scheduler()

    with mock.patch('crawler.scheduler.get_config', _get_config_mock):
        await scheduler.update_config()
        assert scheduler.working_time is True


class BadGrabber(BaseGrabber):
    async def get_in_bids(self):
        raise RuntimeError('Cannot get bids')

    async def get_out_bids(self):
        return []


@pytest.mark.run_loop
async def test_run_task_exceptions(resource, caplog):
    bad_task = BadGrabber(resource=resource)
    scheduler = Scheduler()

    scheduler.add_tasks([bad_task])

    import logging
    with caplog.at_level(logging.INFO):
        await scheduler.run_tasks()

    print('asdf')
    for record in caplog.records:
        print(record)
    print('asdf')
