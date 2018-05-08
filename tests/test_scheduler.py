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


@pytest.mark.run_loop
async def test_working_time():
    scheduler = Scheduler()

    config_invoked = False

    async def _get_config_mock():
        nonlocal config_invoked
        config_invoked = True

        _Config = attr.make_class(
            'Config',
            ['TIME_DAY_STARTS', 'TIME_DAY_ENDS'],
        )
        datetime_starts = datetime.now() - timedelta(hours=1)
        time_starts = datetime_starts.strftime(settings.DEFAULT_TIME_FORMAT)
        datetime_ends = datetime.now() + timedelta(hours=1)
        time_ends = datetime_ends.strftime(settings.DEFAULT_TIME_FORMAT)

        _config = _Config(
            TIME_DAY_STARTS=time_starts,
            TIME_DAY_ENDS=time_ends,
        )
        return _config

    with mock.patch('crawler.scheduler.get_config', _get_config_mock):
        is_working = await scheduler.working_time
        assert is_working is True
        assert config_invoked is True
