import asyncio

import pytest

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

    is_working = await scheduler.working_time
    assert is_working is True
