import pytest

from crawler.factory import Factory


def test_resources_loading():
    f = Factory()
    r = f.load_resources()




@pytest.mark.run_loop
async def test_create_daily_tasks():
    factory = Factory()

    daily_tasks = await factory.create_daily()
