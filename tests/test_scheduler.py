import asyncio

import pytest

from crawler.scheduler import Scheduler, ScheduledTask


@pytest.mark.run_loop
async def test_daily_tasks():
    scheduler = Scheduler()

    async def dummy_task():
        print('Running dummy task...')
        await asyncio.sleep(0.1)

    task = ScheduledTask(dummy_task, '23:45')
    scheduler.add_daily_task(task)

    task.is_ready = lambda: True
    await scheduler.run_daily_tasks()
    assert task.done
