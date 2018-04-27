import pytest

from crawler.factory import Factory


def test_resources_loading():
    f = Factory()
    resources = f.load_resources()

    assert isinstance(resources, list)
    resource = resources[0]

    # Check required fields
    assert hasattr(resource, 'name')
    assert hasattr(resource, 'link')
    assert hasattr(resource, 'urls')


@pytest.mark.run_loop
async def test_create_daily_tasks():
    factory = Factory()

    daily_tasks = await factory.create_daily()
    assert isinstance(daily_tasks, list)
