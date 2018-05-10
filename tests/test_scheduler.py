import asyncio
from unittest import mock
from datetime import datetime, timedelta

import attr
import pytest

import settings
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
    config_invoked = True

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
        REFRESH_PERIOD_MINUTES=1,
    )
    return _config


@pytest.mark.run_loop
async def test_working_time():
    scheduler = Scheduler()

    with mock.patch('crawler.scheduler.get_config', _get_config_mock):
        is_working = await scheduler.working_time
        assert is_working is True


@pytest.mark.run_loop
async def test_task_exceptions():

    async def bad_task():
        print('Running task with exception')
        raise RuntimeError('error occurred')

    async def normal_task():
        print('Running normal task')

    scheduler = Scheduler()

    scheduler.add_tasks([
        bad_task(),
        normal_task(),
    ])

    with mock.patch('crawler.scheduler.get_config', _get_config_mock):
        await scheduler.run_forever()
